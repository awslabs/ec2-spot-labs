#!/usr/bin/python

"""
Licensed under the Amazon Software License (the "License"). You may not use this file
except in compliance with the License. A copy of the License is located at
http://aws.amazon.com/asl/
or in the "license" file accompanying this file. This file is distributed on an "AS IS"
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under the License.'

Simple single-threaded HTTP server used for testing that throttles incoming
requests at 5 TPS.
"""

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import time

class RateLimiter:
    def __init__(self, tps):
        self.tps = tps
        self.tokens = tps
        self.last_time = time.time()

    def should_allow(self):
        cur_time = time.time()
        elapsed_time = cur_time - self.last_time
        self.last_time = cur_time
        new_tokens = elapsed_time * self.tps
        self.tokens = min(self.tps, self.tokens + new_tokens)
        if (self.tokens > 1.0):
            self.tokens -= 1.0
            return True
        else:
            return False

class myHandler(BaseHTTPRequestHandler):
    rate_limiter = RateLimiter(5.0)

    def do_GET(self):
        if (self.__class__.rate_limiter.should_allow()):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write("<html><header><h1>Hello World!</h1></header></html>")
        else:
            self.send_response(429)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write("<html><header><h1>Throttling!</h1></header></html>")
        return

try:
    port = 80
    server = HTTPServer(('', port), myHandler)
    print("Starting simple server")
    server.serve_forever()
except KeyboardInterrupt:
    print("Shutting down simple server")
    server.socket.close()
