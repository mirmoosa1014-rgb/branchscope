import http.client,socket,threading,unittest
from http.server import ThreadingHTTPServer
from branchscope.server import Handler

class ShortTimeoutHandler(Handler):
 timeout=.1
 def log_message(self,*args):pass

class RequestTimeout(unittest.TestCase):
 def test_incomplete_body_returns_timeout_response(self):
  server=ThreadingHTTPServer(('127.0.0.1',0),ShortTimeoutHandler)
  thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with socket.create_connection(server.server_address,timeout=2) as connection:
    connection.sendall(b'POST /api/run HTTP/1.0\r\nContent-Type: application/json\r\nContent-Length: 10\r\n\r\n{')
    response=http.client.HTTPResponse(connection);response.begin()
    self.assertEqual(response.status,408)
  finally:server.shutdown();server.server_close();thread.join()
