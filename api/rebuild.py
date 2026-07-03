"""
api/rebuild.py
Endpoint serverless acionado pelo cron do Vercel às 03:00 UTC.
Também pode ser chamado manualmente via GET /api/rebuild?secret=SEU_SECRET
"""

import os
import sys
import json
import subprocess
from http.server import BaseHTTPRequestHandler

REBUILD_SECRET = os.environ.get("REBUILD_SECRET", "")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Proteção simples por token (opcional, mas recomendado)
        from urllib.parse import urlparse, parse_qs
        params = parse_qs(urlparse(self.path).query)
        secret = params.get("secret", [""])[0]

        # Vercel cron jobs enviam o header Authorization automaticamente
        auth = self.headers.get("Authorization", "")
        is_cron = auth == f"Bearer {os.environ.get('CRON_SECRET', '')}"
        is_manual = REBUILD_SECRET and secret == REBUILD_SECRET

        if not (is_cron or is_manual or not REBUILD_SECRET):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error": "unauthorized"}')
            return

        try:
            script = os.path.join(os.path.dirname(__file__), "..", "scripts", "build.py")
            result = subprocess.run(
                [sys.executable, script],
                capture_output=True, text=True, timeout=120
            )
            body = json.dumps({
                "ok": result.returncode == 0,
                "stdout": result.stdout[-2000:],
                "stderr": result.stderr[-500:] if result.stderr else ""
            })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
