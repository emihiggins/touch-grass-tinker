import io
import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from liftlap.access_check import check, NoRedirect, URL

class Response(io.BytesIO):
    status=200
class Opener:
    def __init__(self, response=None,error=None): self.response=response;self.error=error
    def open(self,request,timeout):
        assert request.full_url==URL
        assert timeout==20
        if self.error: raise self.error
        return Response(json.dumps(self.response).encode())

class AccessTests(unittest.TestCase):
    @patch.dict(os.environ, {'TINKER_API_KEY':'fake-test-only'})
    def test_success(self):
        r=check(Opener({'supported_models':[{'model_name':'Qwen/Qwen3-8B'}]}))
        self.assertTrue(r['verified']);self.assertTrue(r['qwen3_8b_listed']);self.assertFalse(r['billing_verified'])
    @patch.dict(os.environ, {}, clear=True)
    def test_missing(self):self.assertEqual(check()['status'],'missing_credential')
    @patch.dict(os.environ, {'TINKER_API_KEY':'fake-test-only'})
    def test_errors_never_echo_body_or_exception(self):
        e=HTTPError(URL,401,'sensitive response',{},io.BytesIO(b'secret'))
        r=check(Opener(error=e))
        self.assertEqual(r['status'],'authentication_rejected');self.assertNotIn('sensitive',json.dumps(r))
        self.assertEqual(check(Opener(error=RuntimeError('private')))['status'],'transport_error')
    @patch.dict(os.environ, {'TINKER_API_KEY':'fake-test-only'})
    def test_schema_mismatch(self): self.assertFalse(check(Opener({'error':'no models'}))['verified'])
    def test_redirect_blocked(self):self.assertIsNone(NoRedirect().redirect_request(None,None,302,'',{},'https://other.test'))
