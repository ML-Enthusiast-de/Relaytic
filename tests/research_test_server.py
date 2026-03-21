from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


class _ResearchHandler(BaseHTTPRequestHandler):
    semantic_payload: dict = {"data": []}
    crossref_payload: dict = {"message": {"items": []}}
    requests: list[dict] = []

    def log_message(self, format: str, *args) -> None:  # pragma: no cover
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        type(self).requests.append({"path": parsed.path, "query": parsed.query})
        if parsed.path.endswith("/semantic_scholar"):
            payload = type(self).semantic_payload
        elif parsed.path.endswith("/crossref"):
            payload = type(self).crossref_payload
        else:
            self.send_error(404)
            return
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class ResearchTestServer:
    def __init__(self, *, semantic_payload: dict, crossref_payload: dict) -> None:
        _ResearchHandler.semantic_payload = semantic_payload
        _ResearchHandler.crossref_payload = crossref_payload
        _ResearchHandler.requests = []
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), _ResearchHandler)
        self.base_url = f"http://127.0.0.1:{self._server.server_port}"
        self.semantic_url = f"{self.base_url}/semantic_scholar"
        self.crossref_url = f"{self.base_url}/crossref"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def requests(self) -> list[dict]:
        return list(_ResearchHandler.requests)

    def __enter__(self) -> "ResearchTestServer":
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=2)
