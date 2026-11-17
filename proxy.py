#!/usr/bin/env python3
"""buzz-off proxy: sits between goose and the model API, strips the spec'd
blocks out of Buzz's system prompt, passes everything else through (incl. SSE).
  BUZZOFF_UPSTREAM  default https://api.anthropic.com
  BUZZOFF_PORT      default 8787
Point goose at it:  ANTHROPIC_HOST: http://127.0.0.1:8787  (in ~/.config/goose/config.yaml)"""
import json, os, sys, http.client, urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strip_prompt import strip

UP = urllib.parse.urlsplit(os.environ.get("BUZZOFF_UPSTREAM", "https://api.anthropic.com"))
PORT = int(os.environ.get("BUZZOFF_PORT", "8787"))
HOP = {"host", "content-length", "connection", "accept-encoding", "transfer-encoding"}

def rewrite(body: bytes) -> bytes:
    try: req = json.loads(body)
    except Exception: return body
    saved = 0
    def fix(s):
        nonlocal saved
        out = strip(s, strict=False); saved += len(s) - len(out); return out
    sysp = req.get("system")                                  # Anthropic
    if isinstance(sysp, str): req["system"] = fix(sysp)
    elif isinstance(sysp, list):
        for b in sysp:
            if isinstance(b, dict) and isinstance(b.get("text"), str): b["text"] = fix(b["text"])
    for m in req.get("messages", []):                         # OpenAI-style
        if m.get("role") in ("system", "developer") and isinstance(m.get("content"), str):
            m["content"] = fix(m["content"])
    if saved: print(f"stripped {saved} bytes from system prompt", file=sys.stderr, flush=True)
    return json.dumps(req).encode() if saved else body

class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    def log_message(self, *a): pass
    def _go(self):
        body = self.rfile.read(int(self.headers.get("content-length") or 0))
        if body: body = rewrite(body)
        conn = (http.client.HTTPSConnection if UP.scheme == "https" else http.client.HTTPConnection)(UP.netloc, timeout=600)
        hdrs = {k: v for k, v in self.headers.items() if k.lower() not in HOP}
        hdrs["Content-Length"] = str(len(body))
        conn.request(self.command, UP.path.rstrip("/") + self.path, body, hdrs)
        r = conn.getresponse()
        self.send_response(r.status)
        for k, v in r.getheaders():
            if k.lower() not in HOP: self.send_header(k, v)
        self.send_header("Transfer-Encoding", "chunked"); self.end_headers()
        while chunk := r.read1(65536):
            self.wfile.write(b"%x\r\n%s\r\n" % (len(chunk), chunk)); self.wfile.flush()
        self.wfile.write(b"0\r\n\r\n"); conn.close()
    do_POST = do_GET = _go

if __name__ == "__main__":
    print(f"buzz-off proxy :{PORT} -> {UP.geturl()}", file=sys.stderr, flush=True)
    class S(ThreadingHTTPServer):
        daemon_threads = True
        def handle_error(self, req, addr):   # client hung up: not our problem
            if not isinstance(sys.exc_info()[1], (ConnectionError, BrokenPipeError)): super().handle_error(req, addr)
    S(("127.0.0.1", PORT), H).serve_forever()
