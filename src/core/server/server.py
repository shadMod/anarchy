import json
import logging

from typing import Any
from http import HTTPStatus
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger("anarchy_service")

PORT_RANGE = [8000, 6335]
ALLOWED_ORIGINS = ["http://localhost:8080"]


class ServiceRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.mod = None

    def end_headers(self):
        self.send_cors_headers()
        BaseHTTPRequestHandler.end_headers(self)

    def send_cors_headers(self):
        origin = self.headers.get("origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)

    def send_json(self, obj: Any):
        self.send_header("Content-Type", "application/json;charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("UTF-8", "replace"))

    def send_text(self, text: str, content_type: str = "text/plain"):
        self.send_header("Content-Type", f"{content_type};charset=utf-8")
        self.end_headers()
        self.wfile.write(text.encode("UTF-8", "replace"))

    def send_error(self, code: int, message: str = None, explain: str = None):
        try:
            shortmsg, longmsg = self.responses[code]
        except KeyError:
            shortmsg, longmsg = "???", "???"
        if message is None:
            message = shortmsg
        if explain is None:
            explain = longmsg
        self.log_error("code %d, message %s", code, message)
        self.send_response(code, message)
        return self.send_json({"error": message, "explain": explain})

    def handle_request(self) -> None:
        self.send_cors_headers()

        mod = self.dict_router[self.path]
        handler = mod and getattr(mod, "render_template", None)
        if not handler:
            return self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)

        self.send_response(HTTPStatus.ACCEPTED)
        response = handler(self, self)
        if response:
            if isinstance(response, str):
                self.send_text(response)
            else:
                self.send_json(response)

    @property
    def dict_router(self):
        data = {
            key: getattr(self.mod, key) for key in dir(self.mod)
            if not key.startswith("__") and not key.endswith("__")
        }

        router = {
            val[1]: val[0] for val in data["ROUTER"]
        }
        return router

    def do_HEAD(self):
        self.handle_request()

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()


class HTTPServer(ThreadingHTTPServer):
    def __init__(self, mod=None, port=PORT_RANGE[0]):
        cli_service = ServiceRequestHandler
        cli_service.mod = mod
        super().__init__(("localhost", port), ServiceRequestHandler)

    def start(self):
        logger.info(f"🚀 CLI service started at http://localhost:{self.server_port}")
        self.serve_forever()

    def stop(self):
        self.shutdown()
        self.server_close()
