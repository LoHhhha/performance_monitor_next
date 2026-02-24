from http.server import BaseHTTPRequestHandler
import json

from .combiner import Combiner


def send_json_response(
    handler: BaseHTTPRequestHandler, data: dict, status_code: int = 200
):
    payload = json.dumps(data).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(payload)))
    handler.end_headers()
    handler.wfile.write(payload)


class MetricsHandler(BaseHTTPRequestHandler):
    combiner: Combiner | None = None
    endpoint_path = "/info"

    def do_POST(self):
        if self.path != self.endpoint_path:
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            self.rfile.read(content_length)

        try:
            if self.combiner is None:
                raise RuntimeError("Combiner is not initialized")
            data = self.combiner.get_info()
            return_code = 200
        except Exception as exception:
            data = {"err_msg": str(exception)}
            return_code = 500

        send_json_response(self, data, status_code=return_code)

    def do_GET(self):
        self.send_error(405, "Method Not Allowed")
