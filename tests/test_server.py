import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from branchscope.server import Handler

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,method,path,body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=15)
        conn.request(method,path,body,headers or {});r=conn.getresponse();result=(r.status,r.read());conn.close();return result
    def test_live_run(self):
        status,body=self.request('POST','/api/run',json.dumps({'workload':'loop','history':8}),{'Content-Type':'application/json'})
        self.assertEqual(status,200);data=json.loads(body);self.assertEqual(len(data['results']),4)
        for r in data['results']:self.assertEqual(r['count'],5488)
    def test_invalid_requests(self):
        for payload in ['{} garbage','[]','{"history": 0}','{"count": 999999}','{"workload":"missing"}']:
            with self.subTest(payload=payload):self.assertEqual(self.request('POST','/api/run',payload,{'Content-Type':'application/json'})[0],400)
    def test_cross_origin_rejected(self):
        self.assertEqual(self.request('POST','/api/run','{}',{'Content-Type':'application/json','Origin':'https://example.com'})[0],403)
    def test_content_type_and_unknown_route(self):
        self.assertEqual(self.request('POST','/api/run','{}')[0],415)
        self.assertEqual(self.request('POST','/unknown','{}')[0],404)
    def test_app_and_workloads(self):
        self.assertEqual(self.request('GET','/')[0],200)
        status,body=self.request('GET','/api/workloads');self.assertEqual(status,200);self.assertIn('xor',json.loads(body))
