# -*- coding: utf-8 -*-
"""Local static server with optional incremental rebuild for the demo dashboard."""
from __future__ import annotations

import argparse
import json
import mimetypes
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REBUILD_LOCK = threading.Lock()
VERSION = {"value": 0}


def input_signature() -> tuple:
    paths = sorted((ROOT / "demo_input").glob("*.csv"))
    return tuple((path.name, path.stat().st_mtime_ns, path.stat().st_size) for path in paths)


def rebuild() -> None:
    with REBUILD_LOCK:
        for script in ("build_data.py", "generate_html.py"):
            subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=True)
        VERSION["value"] += 1
        print(f"rebuilt dashboard (v{VERSION['value']})", flush=True)


def watch() -> None:
    signature = input_signature()
    while True:
        time.sleep(2)
        current = input_signature()
        if current != signature:
            try:
                rebuild()
                signature = current
            except Exception as exc:  # noqa: BLE001
                print(f"rebuild failed: {exc}", flush=True)


class Handler(BaseHTTPRequestHandler):
    def _send(self, path: Path, content_type: str) -> None:
        try:
            body = path.read_bytes()
        except OSError:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/api/health":
            body = json.dumps({"ok": True, "version": VERSION["value"]}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path in ("/", "/index.html", "/dashboard.html"):
            self._send(ROOT / "dashboard.html", "text/html; charset=utf-8")
            return
        if path == "/api/reload":
            body = json.dumps({"version": VERSION["value"]}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        relative = path.lstrip("/")
        target = (ROOT / relative).resolve()
        if ROOT not in target.parents and target != ROOT:
            self.send_error(403)
            return
        if target.is_file():
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            if content_type.startswith("text/"):
                content_type += "; charset=utf-8"
            self._send(target, content_type)
            return
        self.send_error(404)

    def log_message(self, *_args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the synthetic dashboard locally")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-open", action="store_true")
    parser.add_argument("--no-watch", action="store_true")
    args = parser.parse_args()
    rebuild()
    if not args.no_watch:
        threading.Thread(target=watch, daemon=True).start()
    url = f"http://127.0.0.1:{args.port}"
    print(f"dashboard: {url}", flush=True)
    if not args.no_open:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
