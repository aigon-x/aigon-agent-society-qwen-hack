#!/usr/bin/env python3
"""Serve dashboard on PROD, proxy /api/health to backend."""
import http.server, socketserver, urllib.request, json, os, socket

PORT = int(os.environ.get('DASH_PORT', '8089'))
DIR = os.path.expanduser('~/dashboard')
PROD_HEALTH = 'http://127.0.0.1:7001/health'

class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True
    allow_reuse_port = True
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except OSError:
            pass
        return super().server_bind()

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DIR, **kw)
    def do_GET(self):
        if self.path == '/':
            self.path = '/dashboard.html'
            return super().do_GET()
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            try:
                req = urllib.request.Request(PROD_HEALTH, headers={'User-Agent': 'dashboard/1.0'})
                resp = urllib.request.urlopen(req, timeout=5)
                self.wfile.write(resp.read())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e), "status": "offline"}).encode())
            return
        return super().do_GET()

if __name__ == '__main__':
    with ReuseTCPServer(('', PORT), H) as httpd:
        print(f'Dashboard on 0.0.0.0:{PORT}')
        httpd.serve_forever()
