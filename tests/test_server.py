import unittest,threading,json,urllib.request,urllib.error
from http.server import ThreadingHTTPServer
from liftlap.server import Handler,handle_api
class ServerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.base=f'http://127.0.0.1:{cls.server.server_port}'
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
 def post(self,path,data,**headers):
  req=urllib.request.Request(self.base+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json',**headers});return urllib.request.urlopen(req,timeout=5)
 def test_flow_and_closure(self):
  i=json.load(self.post('/api/interpret',{'text':'only blues, no drag lifts, 45 minutes'}))['intent']
  self.assertEqual(i['status'],'ready')
  r=json.load(self.post('/api/plan',{'intent':i}));self.assertEqual(r['status'],'ok');self.assertTrue(r['validation']['valid'])
  r=json.load(self.post('/api/plan',{'intent':i,'closures':'all_lifts'}));self.assertEqual(r['status'],'no_route')
 def test_unknown_input_abstains(self):
  r=json.load(self.post('/api/interpret',{'text':'fly me to Mars'}));self.assertEqual(r['intent']['status'],'unsupported')
 def test_origin_rejected(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.post('/api/interpret',{},Origin='https://evil.example')
  self.assertEqual(e.exception.code,403);e.exception.close()
 def test_path_and_input(self):
  with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(self.base+'/../../README.md')
  self.assertEqual(e.exception.code,404);e.exception.close()
  with self.assertRaises(urllib.error.HTTPError) as e:self.post('/api/interpret',{'minutes':-1})
  self.assertEqual(e.exception.code,422);e.exception.close()
 def test_oversized(self):
  with self.assertRaises(urllib.error.HTTPError) as e:self.post('/api/interpret',{'text':'x'*17000})
  self.assertEqual(e.exception.code,413);e.exception.close()
 def test_security_headers(self):
  r=urllib.request.urlopen(self.base+'/');self.assertIn("default-src 'self'",r.headers['Content-Security-Policy'])
if __name__=='__main__':unittest.main()
