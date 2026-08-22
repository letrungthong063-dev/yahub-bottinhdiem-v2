"""HTTP health-check server nhỏ, chạy song song để Render.com không tắt worker."""

import os
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger("yahub-bot")


class HealthHandler(BaseHTTPRequestHandler):
    def _respond(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self): self._respond()
    def do_HEAD(self): self._respond()
    def do_POST(self): self._respond()
    def do_OPTIONS(self): self._respond()

    def log_message(self, format, *args):
        pass  # Tắt log HTTP để không rác console


def _run_http():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    logger.info(f"HTTP server chạy tại port {port}")
    server.serve_forever()


def start_health_server():
    threading.Thread(target=_run_http, daemon=True).start()
