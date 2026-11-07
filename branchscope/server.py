"""Loopback-only local demo; no uploads, account, secrets, or paid services."""
import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from .experiment import ROOT, demo
from .workloads import WORKLOADS

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT/'web'),**kwargs)
    def send_json(self,code,value):
        payload=json.dumps(value,allow_nan=False).encode()
        self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(payload)
    def do_GET(self):
        if urlparse(self.path).path=='/api/workloads':return self.send_json(200,WORKLOADS)
        return super().do_GET()
    def do_POST(self):
        if self.path!='/api/run':return self.send_json(404,{'error':'not found'})
        # Browser calls are same-origin. Reject cross-site form/JSON requests.
        origin=self.headers.get('Origin')
        if origin and origin!=f'http://{self.headers.get("Host")}':return self.send_json(403,{'error':'same-origin requests only'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.send_json(415,{'error':'application/json required'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=1024:raise ValueError('request must be 1..1024 bytes')
            args=json.loads(self.rfile.read(length))
            if not isinstance(args,dict) or set(args)-{'workload','seed','budget','history'}:raise ValueError('unsupported request fields')
            result=demo(**args)
        except (ValueError,TypeError) as exc:return self.send_json(400,{'error':str(exc)})
        self.send_json(200,result)

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);a=p.parse_args()
    with ThreadingHTTPServer(('127.0.0.1',a.port),Handler) as server:
        print(f'BranchScope at http://127.0.0.1:{a.port}',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
if __name__=='__main__':main()
