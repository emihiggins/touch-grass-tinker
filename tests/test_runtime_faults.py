"""Offline failures; synthetic provider and temporary budgets only."""
import asyncio
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from liftlap.corpus import read
from liftlap.sample_runner import run_cases, SDKSampler
from liftlap.spend import Ledger


class RuntimeFaultTests(unittest.TestCase):
    def test_deadline_after_acceptance_retains_hold_and_halts(self):
        class Stalled:
            calls = 0
            async def sample(self, tokens, key, callback):
                self.calls += 1
                callback('synthetic-future')
                await asyncio.Event().wait()
        class Tokenizer:
            def decode(self, tokens): return ''
        case = read('benchmark/development-seed.jsonl')[0]
        case['id'] = 'private-case-marker'
        auth = json.loads(Path('training/budget-authorization.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = Ledger(root / 'ledger.sqlite', auth)
            ledger.reconcile_prior(.01, 'synthetic invoice')
            ledger.reserve('run', 'smoke', .7, 'synthetic bound')
            before = ledger.snapshot()
            sampler = Stalled()
            rows = asyncio.run(run_cases([case, case], [[1], [1]], Tokenizer(), [], sampler, root,
                                         'private-run-marker', timeout_seconds=.01))
            self.assertEqual(sampler.calls, 1)
            self.assertEqual(rows[1]['status'], 'not_attempted_after_transport_failure')
            reopened = Ledger(root / 'ledger.sqlite', auth)
            self.assertEqual(reopened.snapshot(), before)
            with self.assertRaises(ValueError):
                reopened.reserve('another', 'smoke', .4, 'must remain blocked')
            raw = (root / 'diagnostics.jsonl').read_text()
            self.assertNotIn('private-', raw)
            self.assertNotIn('synthetic-future', raw)
            diagnostics = read(root / 'diagnostics.jsonl')
            self.assertTrue(diagnostics[0]['accepted_future_observed'])
            self.assertEqual(diagnostics[0]['failure_category'], 'timeout')
            self.assertFalse(diagnostics[0]['automatic_retry'])


@unittest.skipUnless(importlib.util.find_spec('tinker'), 'optional pinned SDK required')
class SDKFaultMatrixTests(unittest.TestCase):
    @patch.dict('os.environ', {'TINKER_API_KEY':'oc-sent-v2.fixture.end', 'HTTPS_PROXY':'http://127.0.0.1:1'})
    def test_no_resubmission_across_failure_matrix(self):
        import httpx
        from liftlap.tinker_sdk import make_client
        case = read('benchmark/development-seed.jsonl')[0]
        class Tokenizer:
            def decode(self, tokens): return 'unused'
        for stage in ('asample', 'retrieve_future'):
            for fault in (429, 503, 404, 'disconnect', 'timeout', 'malformed'):
                with self.subTest(stage=stage, fault=fault), tempfile.TemporaryDirectory() as directory:
                    calls = []
                    def respond(request):
                        endpoint = request.url.path.rsplit('/', 1)[-1]
                        calls.append(endpoint)
                        if endpoint == 'create_session': return httpx.Response(200, json={'session_id':'session-fixture'})
                        if endpoint == 'create_sampling_session': return httpx.Response(200, json={'sampling_session_id':'sampling-fixture'})
                        if endpoint == 'session_heartbeat': return httpx.Response(200, json={})
                        if endpoint == 'asample' and stage != 'asample': return httpx.Response(200, json={'request_id':'future-fixture'})
                        if isinstance(fault, int): return httpx.Response(fault, json={'error':'private-secret-marker'})
                        if fault == 'timeout': raise httpx.ReadTimeout('private-secret-marker', request=request)
                        if fault == 'disconnect': raise httpx.ReadError('private-secret-marker', request=request)
                        return httpx.Response(200, content=b'not-json', headers={'Content-Type':'application/json'})
                    async def run():
                        async with make_client(httpx.MockTransport(respond)) as client:
                            sampler = SDKSampler(client, 'Qwen/Qwen3-8B', None, [], 10, polls=2, poll_interval=0)
                            return await run_cases([case, case], [[1], [1]], Tokenizer(), [], sampler, Path(directory), 'run-fixture')
                    rows = asyncio.run(run())
                    self.assertEqual(calls.count('asample'), 1)
                    self.assertEqual(len(calls), 4 if stage == 'asample' else 5)
                    self.assertEqual(rows[0]['status'], 'transport_or_provider_failure')
                    self.assertEqual(rows[1]['status'], 'not_attempted_after_transport_failure')
                    raw = Path(directory, 'diagnostics.jsonl').read_text()
                    self.assertNotIn('private-secret-marker', raw)
                    self.assertNotIn('oc-sent', raw)
                    diagnostics = read(Path(directory, 'diagnostics.jsonl'))
                    self.assertEqual(diagnostics[0]['accepted_future_observed'], stage != 'asample')
                    expected = {429:'rate_limited', 503:'provider_5xx', 404:'provider_4xx', 'timeout':'timeout'}.get(fault, 'transport_or_response_failure')
                    self.assertEqual(diagnostics[0]['failure_category'], expected)
                    self.assertNotIn(case['request_text'], raw)

class ProcessBudgetTests(unittest.TestCase):
    def test_process_exit_after_reservation_preserves_hold(self):
        import subprocess
        import sys
        auth = json.loads(Path('training/budget-authorization.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ledger.sqlite'
            ledger = Ledger(path, auth)
            ledger.reconcile_prior(.01, 'synthetic invoice')
            program = """import json,os,sys
from pathlib import Path
from liftlap.spend import Ledger
ledger=Ledger(sys.argv[1],json.loads(Path('training/budget-authorization.json').read_text()))
ledger.reserve('crashed-run','smoke',.7,'synthetic pending request')
os._exit(17)
"""
            result = subprocess.run([sys.executable, '-c', program, str(path)], timeout=10)
            self.assertEqual(result.returncode, 17)
            restarted = Ledger(path, auth)
            self.assertEqual(restarted.snapshot()['unresolved'], 1)
            self.assertAlmostEqual(restarted.snapshot()['committed_usd'], .71)
            with self.assertRaises(ValueError):
                restarted.reserve('new-run', 'smoke', .4, 'must remain blocked')

    def test_distinct_processes_cannot_overreserve(self):
        import subprocess
        import sys
        auth = json.loads(Path('training/budget-authorization.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'ledger.sqlite'
            Ledger(path, auth).reconcile_prior(.01, 'synthetic invoice')
            program = """import json,sys
from pathlib import Path
from liftlap.spend import Ledger
ledger=Ledger(sys.argv[1],json.loads(Path('training/budget-authorization.json').read_text()))
try: ledger.reserve(sys.argv[2],'smoke',.6,'synthetic concurrent attempt')
except ValueError: sys.exit(3)
"""
            processes = [subprocess.Popen([sys.executable, '-c', program, str(path), str(i)]) for i in range(2)]
            self.assertEqual(sorted(p.wait(timeout=10) for p in processes), [0, 3])
            self.assertAlmostEqual(Ledger(path, auth).snapshot()['committed_usd'], .61)

class OfflineRecoveryTests(unittest.TestCase):
    def test_failed_live_session_can_use_offline_without_resubmission(self):
        import threading
        from unittest.mock import AsyncMock, Mock
        from liftlap.app_model import LiveModel, ModelUnavailable
        from liftlap.server import handle_api
        with tempfile.TemporaryDirectory() as directory:
            model = LiveModel.__new__(LiveModel)
            model.lock = threading.Lock()
            model.halted = False
            model.attempts = 0
            model.directory = Path(directory)
            model.prompt = 'synthetic fixture'
            model.renderer = Mock()
            model.renderer.build_generation_prompt.return_value.to_ints.return_value = [1]
            model._run = AsyncMock(return_value={'status':'transport_or_provider_failure'})
            payload = {'adapter':'live', 'text':'only blues'}
            with self.assertRaises(ModelUnavailable): handle_api('/api/interpret', payload, model)
            with self.assertRaises(ModelUnavailable): handle_api('/api/interpret', payload, model)
            self.assertEqual(model.attempts, 1)
            model._run.assert_awaited_once()
            offline = handle_api('/api/interpret', {'adapter':'rules', 'text':'only blues'}, model)
            self.assertEqual(offline['adapter'], 'rules-v2')
            self.assertTrue(offline['semantic_validation']['plan_allowed'])
            self.assertNotIn('route', offline)
            model._run.assert_awaited_once()
