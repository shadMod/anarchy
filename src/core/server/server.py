# Source code of Anarchy Framework
# Copyright (C) 2023 shadMod <info@shadmod.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

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

    def send_text(self, text: str, content_type: str = "text/plain"):
        self.send_header("Content-Type", f"{content_type};charset=utf-8")
        self.end_headers()
        self.wfile.write(text.encode("UTF-8", "replace"))

    def send_bytes(self, text: bytes, content_type: str = "text/html"):
        # self.send_response(STATUS_OK)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(text)

    def send_json(self, obj: dict, content_type: str = "application/json"):
        self.send_header("Content-Type", f"{content_type};charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("UTF-8", "replace"))

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
        render = mod().render_template

        # handler = mod and getattr(mod, "render_template", None)
        # if not handler:
        #     return self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)

        if not render:
            return self.send_error(HTTPStatus.METHOD_NOT_ALLOWED)
        self.send_response(HTTPStatus.ACCEPTED)

        if render:
            if isinstance(render, bytes):
                self.send_bytes(render)
            elif isinstance(render, str):
                self.send_text(render)
            else:
                self.send_json(render)

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
        logger.info(f"🚀 Service started at http://localhost:{self.server_port}")
        self.serve_forever()

    def stop(self):
        self.shutdown()
        self.server_close()
