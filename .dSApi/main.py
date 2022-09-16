import json
import time
import numpy as np
import csv
import http.server
import socketserver
from typing import Tuple
from http import HTTPStatus

url = '/getaccounts?account='
class Handler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        super().__init__(request, client_address, server)
        

    @property
    def api_response(self) -> json:
        if len(self.path.split("=")[1]) > 0:
            self.account_id = self.path.split("=")[1]
            self.start = time.time()
            # count data rows, to preallocate array
            f = open('links.csv', 'rb')
            def count(f):
                while 1:
                    block = f.read(65536)
                    if not block:
                         break
                    yield block.count(',')
            linecount = sum(count(f))
            print('\n%.3fs: file has %s rows') % (self.elapsed(), linecount)

            # pre-allocate array and load data into array
            m = np.zeros(linecount, dtype=[('a', np.uint32), ('b', np.uint32)])
            f.seek(0)
            f = csv.reader(open('links.csv', 'rb'))
            for i, row in enumerate(f):
                m[i] = int(row[0]), int(row[1])

            print('%.3fs: loaded') % self.elapsed()
            # sort in-place
            m.sort(order='b')

            print('%.3fs: sorted') % self.elapsed()

        return json.dumps({"account_id": self.path}).encode()
    def do_GET(self) -> None:
        if self.path.startswith(url):
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(self.api_response))
    def elapsed(self):
        return time.time() - self.start


if __name__ == "__main__":
    PORT = 8080
    # Create an object of the above class
    my_server = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
    # Start the server
    print(f"Server started at localhost:{PORT}{url}")
    my_server.serve_forever()