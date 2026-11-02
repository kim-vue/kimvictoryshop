"""Loopback-only demonstration transport; no filesystem or admin API.

The actor selector controls five equal-rights simulated subjects. It is not an
authentication UI or a production MASTER approval system. Every operation below
uses a genuine credentialed Zoombar created by the isolated demo fixture.
"""

from __future__ import annotations

from hmac import compare_digest
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
from threading import RLock
from urllib.parse import parse_qs, urlsplit

from .core import ZoomError
from .demo import Demo, create_demo
from .execution import ExecutionError


class DemoApplication:
    def __init__(self, demo: Demo):
        self.demo = demo
        self.lock = RLock()

    def state(self, actor: str = "USER", **extra):
        bar = self.demo.bars[actor]
        return {
            "actor": actor,
            "actors": list(self.demo.bars),
            "here": bar.here(),
            "path": bar.path(),
            "url": bar.url(),
            "visible": bar.see(),
            "nodes": self.demo.nodes,
            "links": self.demo.links,
            "bookmarks": bar.bookmarks(),
            "contracts": bar.contracts(),
            "history": bar.history(),
            "integrity": self.demo.world.verify_history(),
            **extra,
        }

    def enter(self, bar, payload):
        bar.zoom_in(payload["target"], connection_id=payload.get("connection_id"))
        return {}

    def out(self, bar, payload):
        return {"status": bar.zoom_out()}

    def root(self, bar, payload):
        bar.zoom_root()
        return {}

    def bookmark(self, bar, payload):
        bar.bookmark(payload["name"])
        return {}

    def walk(self, bar, payload):
        bar.walk(payload["url"])
        return {}

    def run(self, bar, payload):
        contract = payload["contract"]
        request = {key: contract[key] for key in (
            "BASE_PIN", "COMMON_ACTION", "INNER_LENS", "UNIQUE_ACTION"
        )}
        request["data"] = payload["data"]
        parameter_hash = bar.put(request)
        returned = bar.run(parameter_hash)
        done = next(event for event in bar.history() if event["kind"] == "CYCLE_DONE")
        result_hash = done["body"]["result_hash"]
        return {
            "last_result": bar.read(result_hash),
            "parameter_hash": parameter_hash,
            "result_hash": result_hash,
            "returned_none": returned is None,
        }

    def perform(self, payload):
        if not isinstance(payload, dict):
            raise ZoomError("BAD_REQUEST", "명령은 JSON 객체여야 합니다.")
        actor = payload.get("actor", "USER")
        if actor not in self.demo.bars:
            raise ZoomError("UNKNOWN_ACTOR", "데모에 등록된 주체를 선택하세요.")
        # Transport command allowlist, never LENS-kind dispatch or getattr/eval.
        commands = {
            "enter": self.enter, "out": self.out, "root": self.root,
            "bookmark": self.bookmark, "walk": self.walk, "run": self.run,
        }
        command = commands.get(payload.get("action"))
        if command is None:
            raise ZoomError("UNKNOWN_COMMAND", "지원하지 않는 데모 명령입니다.")
        extra = command(self.demo.bars[actor], payload)
        return self.state(actor, **extra)


class DemoServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, application):
        self.application = application
        self.session_secret = secrets.token_urlsafe(32)
        super().__init__(address, DemoHandler)


class DemoHandler(BaseHTTPRequestHandler):
    server: DemoServer
    server_version = "ZOOMCONNECT/0.1"

    def handle(self):
        try:
            super().handle()
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            # A browser or local client may disconnect during headers or body.
            # This request cannot receive another response; end it quietly.
            self.close_connection = True

    def log_message(self, format, *args):
        # Do not log request bodies, credentials, cookies or HASH payloads.
        return

    def _host_ok(self):
        port = self.server.server_port
        return self.headers.get("Host", "") in {f"127.0.0.1:{port}", f"localhost:{port}"}

    def _session_ok(self):
        try:
            cookies = SimpleCookie(self.headers.get("Cookie", ""))
            token = cookies.get("zc_demo")
            return token is not None and compare_digest(token.value, self.server.session_secret)
        except (ValueError, TypeError):
            return False

    def _send(self, code, body, content_type="application/json; charset=utf-8", cookie=False):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        if cookie:
            self.send_header("Set-Cookie", f"zc_demo={self.server.session_secret}; HttpOnly; SameSite=Strict; Path=/")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, value):
        body = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self._send(code, body)

    def _error(self, code, message, status=400):
        self._json(status, {"error": {"code": code, "message": message}})

    def do_GET(self):
        if not self._host_ok():
            self._error("HOST_DENIED", "로컬 주소로 접속하세요.", 403)
            return
        parsed = urlsplit(self.path)
        if parsed.path == "/":
            html = Path(__file__).with_name("web").joinpath("index.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8", cookie=True)
            return
        if parsed.path != "/api/state":
            self._error("NOT_FOUND", "경로가 없습니다.", 404)
            return
        if not self._session_ok():
            self._error("SESSION_REQUIRED", "먼저 데모 화면을 열어 주세요.", 403)
            return
        actor = parse_qs(parsed.query).get("actor", ["USER"])[0]
        application = self.server.application
        with application.lock:
            if actor not in application.demo.bars:
                self._error("UNKNOWN_ACTOR", "등록되지 않은 데모 주체입니다.")
                return
            self._json(200, application.state(actor))

    def do_POST(self):
        if not self._host_ok() or not self._session_ok():
            self._error("SESSION_REQUIRED", "로컬 데모 세션이 필요합니다.", 403)
            return
        port = self.server.server_port
        if self.headers.get("Origin", "") not in {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}:
            self._error("ORIGIN_DENIED", "외부 페이지의 명령은 허용하지 않습니다.", 403)
            return
        if urlsplit(self.path).path != "/api/action":
            self._error("NOT_FOUND", "경로가 없습니다.", 404)
            return
        if self.headers.get_content_type() != "application/json":
            self._error("JSON_REQUIRED", "JSON 명령을 사용하세요.", 415)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 1_048_576:
                self._error("BAD_LENGTH", "명령 크기가 허용 범위를 벗어났습니다.", 413)
                return
            # Reject non-standard JSON floats before they reach the shared core.
            def reject_constant(value):
                raise ValueError(f"허용하지 않는 JSON 숫자: {value}")
            payload = json.loads(self.rfile.read(length), parse_constant=reject_constant)
            application = self.server.application
            with application.lock:
                self._json(200, application.perform(payload))
        except (ZoomError, ExecutionError) as error:
            self._error(error.code, error.message)
        except (ValueError, KeyError, TypeError, StopIteration, RecursionError):
            self._error("BAD_REQUEST", "명령의 필드와 자료형을 확인하세요.")


def make_server(port=0):
    demo = create_demo()
    return DemoServer(("127.0.0.1", port), DemoApplication(demo))


def serve_demo(port=8765):
    server = make_server(port)
    print(f"ZOOMCONNECT 로컬 데모 — http://127.0.0.1:{server.server_port}")
    print("격리된 예제 데이터만 사용합니다. 종료: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        server.application.demo.world.close()
