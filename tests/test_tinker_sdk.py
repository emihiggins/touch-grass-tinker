import asyncio
import importlib.util
import os
import unittest
from unittest.mock import patch

@unittest.skipUnless(importlib.util.find_spec('tinker'), 'optional pinned SDK environment required')
class SDKTests(unittest.TestCase):
    @patch.dict(os.environ,{'TINKER_API_KEY':'plaintext-not-allowed','HTTPS_PROXY':'http://127.0.0.1:1'})
    def test_rejects_plaintext(self):
        from liftlap.tinker_sdk import make_client
        with self.assertRaises(RuntimeError):make_client()
    @patch.dict(os.environ,{'TINKER_API_KEY':'oc-sent-v2.fixture.end','HTTPS_PROXY':'http://127.0.0.1:1'})
    def test_mock_request_preserves_sentinel_and_destination(self):
        import httpx
        from liftlap.tinker_sdk import make_client,BASE_URL
        requests=[]
        def respond(req):
            requests.append(req)
            return httpx.Response(200,json={'supported_models':[{'model_name':'Qwen/Qwen3-8B'}]})
        async def run():
            async with make_client(httpx.MockTransport(respond)) as c:
                r=await c.service.get_server_capabilities()
                m=r.supported_models[0]
                self.assertEqual(m['model_name'] if isinstance(m,dict) else m.model_name,'Qwen/Qwen3-8B')
        asyncio.run(run())
        self.assertEqual(str(requests[0].url),BASE_URL+'/api/v1/get_server_capabilities')
        self.assertEqual(requests[0].headers['X-API-Key'],'oc-sent-v2.fixture.end')
    @patch.dict(os.environ,{'TINKER_API_KEY':'oc-sent-v2.fixture.end','HTTPS_PROXY':'http://127.0.0.1:1'})
    def test_redirect_not_followed(self):
        import httpx
        from liftlap.tinker_sdk import make_client
        requests=[]
        def respond(req):
            requests.append(req);return httpx.Response(302,headers={'Location':'https://elsewhere.invalid'})
        async def run():
            async with make_client(httpx.MockTransport(respond)) as c:
                with self.assertRaises(Exception): await c.service.get_server_capabilities()
        asyncio.run(run());self.assertEqual(len(requests),1)
