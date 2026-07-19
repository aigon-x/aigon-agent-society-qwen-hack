#!/usr/bin/env python3
"""Dashboard server: serves static files + proxies /api/health -> runtime with CORS."""
import http.server, urllib.request, json, os, sys

RUNTIME = 'http://127.0.0.1:7000'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            try:
                req = urllib.request.Request(RUNTIME + '/health')
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'Runtime unavailable: ' + str(e).encode())
        elif self.path == '/':
            self.path = '/dashboard.html'
            super().do_GET()
        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        pass  # quiet

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = http.server.HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print(f'Serving on 0.0.0.0:{PORT} (proxy -> {RUNTIME})')
    server.serve_forever()
