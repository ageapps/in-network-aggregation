#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler
from routes import routes


class Server(BaseHTTPRequestHandler):
    """Server
    """
    def do_HEAD(self):
        return

    def do_POST(self):
        return

    def do_GET(self):
        self.respond()

    def handle_http(self, status, content_type):
        content_type = "text/plain"
        response_content = ""

        if self.path in routes:
            response_content = routes[self.path]
        else:
            response_content = "404 Not Found"

        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()
        return bytes(response_content, "UTF-8")

    def respond(self):
        content = self.handle_http(200, "text/html")
        self.wfile.write(content)
