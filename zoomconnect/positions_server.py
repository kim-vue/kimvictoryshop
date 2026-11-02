"""Loopback demo: ordered collections, positional identities, one ZOOMBAR."""

from pathlib import Path
from threading import RLock
from http.server import ThreadingHTTPServer
import secrets
from urllib.parse import urlsplit

from .core import ZoomError
from .positional import Address, PositionalError
from .positions_demo import create_position_demo
from .server import DemoHandler


class PositionApplication:
    def __init__(self, demo):
        self.demo = demo
        self.lock = RLock()

    def state(self, actor="USER", **extra):
        bar = self.demo.bars[actor]
        # A layout edit may invalidate a different actor's previously visited
        # entry. Recovery still uses that actor's genuine ZOOMBAR, never a UID.
        status = None
        try:
            view = bar.view()
        except PositionalError as error:
            if error.code != "STALE_PATH":
                raise ZoomError(error.code, error.message) from error
            status = bar.out()
            view = bar.view()
        return {
            "actor": actor,
            "actors": list(self.demo.bars),
            "here": bar.here().as_list(),
            "current": bar.current(),
            "path": [a.as_list() for a in bar.path()],
            "url": bar.url(),
            "view": view,
            "collections": self.demo.collections,
            "bookmarks": bar.bookmarks(),
            "zoombar": bar.zoombar_view(),
            "history": bar.history(),
            "contracts": bar.contracts(),
            "workspace": self.demo.workspaces[actor].as_list(),
            "workspace_entry": self.demo.workspace_entries[actor],
            "mix_targets": self.demo.mix_targets[actor],
            "integrity": self.demo.world.verify_history(),
            "status": status,
            **extra,
        }

    def open(self, bar, payload):
        bar.open(payload["position"], payload["expected_revision"])
        return {}

    def out(self, bar, payload):
        return {"status": bar.out()}

    def root(self, bar, payload):
        bar.root()
        return {}

    def walk(self, bar, payload):
        bar.walk(payload["url"])
        return {}

    def bookmark(self, bar, payload):
        bar.bookmark(payload["collection"], payload["position"], payload["expected_revision"])
        return {}

    def reorder(self, bar, payload):
        if payload["collection"] != bar.here().collection:
            raise ZoomError("NOT_CURRENT_COLLECTION", "현재 ZOOMBAR의 목록에서만 위치를 바꿀 수 있습니다.")
        bar.reorder(payload["from_position"], payload["to_position"], payload["expected_revision"])
        return {"status": "REORDERED"}

    def run(self, bar, payload):
        contract = payload["contract"]
        parameter = {field: contract[field] for field in (
            "BASE_PIN", "COMMON_ACTION", "INNER_LENS", "UNIQUE_ACTION"
        )}
        parameter["data"] = payload["data"]
        parameter_hash = bar.put(parameter)
        returned = bar.run(parameter_hash)
        result_hash = bar.last_result_hash()
        return {
            "parameter_hash": parameter_hash,
            "result_hash": result_hash,
            "last_result": bar.read(result_hash),
            "returned_none": returned is None,
        }

    @staticmethod
    def address(value):
        if not isinstance(value, list) or len(value) != 2:
            raise ZoomError("BAD_ADDRESS", "위치는 [컬렉션 번호, 칸 번호]여야 합니다.")
        return Address(*value)

    def connect(self, bar, payload):
        address = bar.connect(self.address(payload["target"]), payload["title"],
                              payload["expected_revision"], position=payload.get("position"))
        return {"status": "CONNECTED", "changed_slot": address.as_list()}

    def mix(self, bar, payload):
        entries = payload["entries"]
        if not isinstance(entries, list):
            raise ZoomError("BAD_ENTRIES", "혼합할 연결 목록이 필요합니다.")
        if any(not isinstance(entry, dict) or set(entry) != {"target", "title"} for entry in entries):
            raise ZoomError("BAD_ENTRY", "각 연결에는 title과 target만 지정하세요.")
        prepared = [{"target": self.address(entry["target"]), "title": entry["title"]} for entry in entries]
        addresses = bar.mix(prepared, payload["expected_revision"])
        return {"status": "MIXED", "changed_slots": [address.as_list() for address in addresses]}

    def separate(self, bar, payload):
        bar.separate(payload["position"], payload["expected_revision"])
        return {"status": "SEPARATED", "changed_slot": [bar.here().collection, payload["position"]]}

    def reconnect(self, bar, payload):
        target = self.address(payload["target"]) if "target" in payload else None
        address = bar.reconnect(payload["position"], payload["expected_revision"],
                                target=target, title=payload.get("title"))
        return {"status": "RECONNECTED", "changed_slot": address.as_list()}

    def perform(self, payload):
        if not isinstance(payload, dict):
            raise ZoomError("BAD_REQUEST", "명령은 JSON 객체여야 합니다.")
        actor = payload.get("actor", "USER")
        if actor not in self.demo.bars:
            raise ZoomError("UNKNOWN_ACTOR", "등록된 데모 주체를 선택하세요.")
        # This is an HTTP command allowlist, not a collection-kind dispatch.
        commands = {
            "open": self.open, "out": self.out, "root": self.root,
            "walk": self.walk, "bookmark": self.bookmark, "reorder": self.reorder,
            "run": self.run,
            "connect": self.connect, "mix": self.mix,
            "separate": self.separate, "reconnect": self.reconnect,
        }
        command = commands.get(payload.get("action"))
        if command is None:
            raise ZoomError("UNKNOWN_COMMAND", "지원하지 않는 명령입니다.")
        try:
            extra = command(self.demo.bars[actor], payload)
            return self.state(actor, **extra)
        except PositionalError as error:
            raise ZoomError(error.code, error.message) from error


class PositionHandler(DemoHandler):
    server_version = "ZOOMCONNECT/0.3"

    def do_GET(self):
        if urlsplit(self.path).path == "/":
            if not self._host_ok():
                self._error("HOST_DENIED", "로컬 주소로 접속하세요.", 403)
                return
            html = Path(__file__).with_name("web").joinpath("positions.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8", cookie=True)
            return
        super().do_GET()


class PositionServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, application):
        self.application = application
        self.session_secret = secrets.token_urlsafe(32)
        super().__init__(address, PositionHandler)


def make_position_server(port=0):
    return PositionServer(("127.0.0.1", port), PositionApplication(create_position_demo()))


def serve_positions(port=8765):
    server = make_position_server(port)
    print(f"ZOOMCONNECT 위치 기반 컬렉션 데모 — http://127.0.0.1:{server.server_port}")
    print("격리된 예제입니다. 위치가 신원이며, 종류별 이동 분기를 사용하지 않습니다. 종료: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        server.application.demo.world.close()
