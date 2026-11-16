#!/usr/bin/env python3
"""Throwaway local proxy: serves the obfuscated bundle in place of Shiba's,
proxying everything else to the live site so the app still authenticates."""
import http.server, socketserver, urllib.request, urllib.error, sys, os, re

TARGET = "https://shiba-bank.com"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
      "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148")
OBF = "/Users/kirniy/dev/vvnvc-vendor/.build/out.js"
CSS = "/Users/kirniy/dev/vvnvc-vendor/.build/obf.css"
BUNDLE = re.compile(r"^/app/a/app\.[0-9a-f]+\.js")
LOG = []
STUB = open("/Users/kirniy/dev/vvnvc-vendor/.build/stub.js").read()


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _proxy(self, method):
        path = self.path
        if path.split("?")[0].endswith("stub_v3.js"):
            LOG.append("SERVED_STUB")
            return self._send(200, STUB.encode(), "application/javascript")
        if re.match(r"^/app/a/app\.[0-9a-f]+\.css", path.split("?")[0]):
            LOG.append("SERVED_CSS")
            return self._send(200, open(CSS, "rb").read(), "text/css")
        if BUNDLE.match(path.split("?")[0]):
            LOG.append("SERVED_OBF")
            return self._send(200, open(OBF, "rb").read(), "application/javascript")
        body = None
        if method == "POST":
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        req = urllib.request.Request(TARGET + path, data=body, method=method)
        for h in ("Content-Type", "X-Telegram-Init-Data", "Accept"):
            if self.headers.get(h):
                req.add_header(h, self.headers[h])
        req.add_header("User-Agent", UA)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                if "text/html" in (r.headers.get("Content-Type") or ""):
                    data = data.replace(b"telegram-web-app-124bdff7.js",
                                        b"stub_v3.js")
                self.send_response(r.status)
                for k, v in r.headers.items():
                    if k.lower() in ("content-type", "cache-control"):
                        self.send_header(k, v)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                if "/api/" in path:
                    LOG.append(f"{method} {path.split('?')[0]} -> {r.status}")
        except urllib.error.HTTPError as e:
            d = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "text/plain"))
            self.send_header("Content-Length", str(len(d)))
            self.end_headers()
            self.wfile.write(d)
            LOG.append(f"{method} {path.split('?')[0]} -> {e.code}")

    def do_GET(self):
        self._proxy("GET")

    def do_POST(self):
        self._proxy("POST")


class S(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8901
    print(f"proxy on {port}", flush=True)
    S(("127.0.0.1", port), H).serve_forever()
