"""
Main Application Server.
Multi-threaded HTTP Server bridging REST API routing and frontend static asset delivery.
"""

import os
import mimetypes
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote

from backend.config import HOST, PORT, FRONTEND_DIR
from backend.database import init_db
from backend.routes import dispatch_api_request

class EnergyDetectiveHandler(SimpleHTTPRequestHandler):
    """Handles both REST API endpoints and static frontend SPA assets."""

    def __init__(self, *args, **kwargs):
        # Configure static directory
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def log_message(self, format, *args):
        # Clean logging format
        print(f"[{self.log_date_time_string()}] {self.command} {self.path} - {format % args}")

    def do_OPTIONS(self):
        if not dispatch_api_request(self, "OPTIONS", self.path):
            self.send_response(204)
            self.end_headers()

    def do_GET(self):
        if dispatch_api_request(self, "GET", self.path):
            return
        self.serve_frontend_file()

    def do_POST(self):
        if dispatch_api_request(self, "POST", self.path):
            return
        self.send_error(404, "Not Found")

    def do_PUT(self):
        if dispatch_api_request(self, "PUT", self.path):
            return
        self.send_error(404, "Not Found")

    def do_DELETE(self):
        if dispatch_api_request(self, "DELETE", self.path):
            return
        self.send_error(404, "Not Found")

    def serve_frontend_file(self):
        """Serves static files from frontend/ directory with SPA index.html fallback."""
        clean_path = unquote(self.path.split("?")[0]).lstrip("/")
        if not clean_path:
            clean_path = "index.html"

        file_path = FRONTEND_DIR / clean_path

        # If file doesn't exist, serve index.html for Single Page Application routing
        if not file_path.exists() or file_path.is_dir():
            file_path = FRONTEND_DIR / "index.html"

        if not file_path.exists():
            self.send_error(404, "File Not Found")
            return

        # Determine MIME type
        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            content_type = "application/octet-stream"
        if content_type.startswith("text/") or content_type in ("application/javascript", "application/json"):
            content_type += "; charset=utf-8"

        try:
            content = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache, must-revalidate")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(content)
        except Exception as err:
            self.send_error(500, f"Error reading file: {str(err)}")

def create_server(host: str = HOST, port: int = PORT) -> ThreadingHTTPServer:
    """Initializes the database and configures the HTTP server."""
    init_db()
    server = ThreadingHTTPServer((host, port), EnergyDetectiveHandler)
    return server

def run_server(host: str = HOST, port: int = PORT) -> None:
    """Launches the server with fallback port handling."""
    init_db()
    actual_port = port
    server = None
    for attempt in range(10):
        try:
            server = ThreadingHTTPServer((host, actual_port), EnergyDetectiveHandler)
            break
        except OSError:
            actual_port += 1

    if not server:
        raise RuntimeError(f"Could not bind to any port starting from {port}")

    print(f"==================================================")
    print(f"  [ENERGY DETECTIVE] Server Active")
    print(f"  Host: http://{host}:{actual_port}")
    print(f"  API:  http://{host}:{actual_port}/api")
    print(f"==================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Energy Detective Server...")
        server.shutdown()
        server.server_close()

if __name__ == "__main__":
    run_server()
