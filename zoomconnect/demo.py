"""An explicit demo fixture, never a branch in the shared movement engine.

All business names below are sample data. No package is downloaded, no third-party
software is analysed, and no external account is accessed by this fixture.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .core import World


@dataclass
class Demo:
    world: World
    bars: dict[str, Any]
    nodes: list[dict[str, str]]
    links: list[dict[str, str]]
    contracts: list[dict[str, Any]]
    bookmarks: list[dict[str, str]]


def create_demo(database: str | Path = ":memory:") -> Demo:
    """Create a new isolated sample world. Refuse reuse of an existing database."""
    world = World(str(database))
    master_key = world.setup()
    admin = world.admin(master_key)
    nodes = [
        {"uid": "MASTER", "label": "출발 세계", "kind": "MASTER"},
        {"uid": "DELIVERY", "label": "배달", "kind": "WORLD"},
        {"uid": "COUPANG", "label": "쿠팡", "kind": "SERVICE"},
        {"uid": "BAEMIN", "label": "배민", "kind": "SERVICE"},
        {"uid": "LAYER_DELIVERY", "label": "배달 레이어", "kind": "LAYER"},
        {"uid": "BRIDGE_GPS_A", "label": "위치 연결 A", "kind": "BRIDGE"},
        {"uid": "BRIDGE_GPS_B", "label": "위치 연결 B", "kind": "BRIDGE"},
        {"uid": "GPS", "label": "위치", "kind": "WORLD"},
        {"uid": "ARCHIVE", "label": "보관함", "kind": "STORAGE"},
    ]
    for node in nodes[1:]:
        admin.lens(**node)
    pairs = [
        ("MASTER", "DELIVERY"),
        ("MASTER", "ARCHIVE"),
        ("DELIVERY", "COUPANG"),
        ("DELIVERY", "BAEMIN"),
        ("DELIVERY", "LAYER_DELIVERY"),
        ("COUPANG", "LAYER_DELIVERY"),
        ("BAEMIN", "LAYER_DELIVERY"),
        ("LAYER_DELIVERY", "GPS"),
        ("DELIVERY", "BRIDGE_GPS_A"),
        ("DELIVERY", "BRIDGE_GPS_B"),
        ("BRIDGE_GPS_A", "GPS"),
        ("BRIDGE_GPS_B", "GPS"),
    ]
    links = []
    for index, (source, target) in enumerate(pairs):
        uid = admin.connect(source, target, connection_id=f"demo-edge-{index:02d}")
        links.append({"uid": uid, "source": source, "target": target})
    contracts = [
        {
            "BASE_PIN": "DELIVERY",
            "COMMON_ACTION": "정산",
            "INNER_LENS": "COUPANG",
            "UNIQUE_ACTION": "일별 합계",
            "version": 1,
            "algorithm": "total",
            "input_type": "number_list",
        },
        {
            "BASE_PIN": "DELIVERY",
            "COMMON_ACTION": "정산",
            "INNER_LENS": "BAEMIN",
            "UNIQUE_ACTION": "일별 합계",
            "version": 1,
            "algorithm": "total",
            "input_type": "number_list",
        },
    ]
    for contract in contracts:
        admin.contract(contract)
    bookmarks = [
        {"name": "쿠팡 정산", "target": "COUPANG"},
        {"name": "배민 정산", "target": "BAEMIN"},
        {"name": "위치 찾기", "target": "GPS"},
    ]
    bars = {}
    for name in ("USER", "AI", "MASTER", "AGENT", "CODE"):
        # These are equal-rights demo subjects, not a browser role-escalation API.
        key = admin.actor(name)
        for node in nodes:
            admin.grant(key, node["uid"])
        for bookmark in bookmarks:
            admin.bookmark(key, bookmark["name"], bookmark["target"])
        bars[name] = world.zoombar(key)
    return Demo(world, bars, nodes, links, contracts, bookmarks)


def run_demo() -> dict[str, Any]:
    demo = create_demo()
    world = demo.world
    try:
        user = demo.bars["USER"]
        code = demo.bars["CODE"]
        user.bookmark("쿠팡 정산")
        before = user.path()
        request = {
            "BASE_PIN": "DELIVERY",
            "COMMON_ACTION": "정산",
            "INNER_LENS": "COUPANG",
            "UNIQUE_ACTION": "일별 합계",
            "data": [4500, 3800, 5200],
        }
        parameter_hash = user.put(request)
        returned = user.run(parameter_hash)
        done = next(event for event in reversed(user.history()) if event["kind"] == "CYCLE_DONE")
        result = user.read(done["body"]["result_hash"])
        code.walk("zoom://world/MASTER/DELIVERY/BRIDGE_GPS_A/GPS")
        code_path = code.path()
        code.zoom_out()
        return {
            "user_path": before,
            "code_path": code_path,
            "code_after_out": code.path(),
            "user_path_unchanged": user.path() == before,
            "cycle_returned_none": returned is None,
            "calculation": result,
            "history": world.verify_history(),
        }
    finally:
        world.close()
