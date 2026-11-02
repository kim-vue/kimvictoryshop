"""Position-identity collection fixture. No hidden per-LENS identifier is used."""

from dataclasses import dataclass
from typing import Any

from .positional import Address, PositionalWorld


@dataclass
class PositionDemo:
    world: PositionalWorld
    bars: dict[str, Any]
    collections: list[dict[str, Any]]
    places: dict[str, Address]
    workspaces: dict[str, Address]
    workspace_entries: dict[str, int]
    mix_targets: dict[str, list[dict[str, Any]]]


def create_position_demo(database=":memory:") -> PositionDemo:
    world = PositionalWorld(database)
    master_key = world.setup()
    admin = world.admin(master_key)
    places = {"root": Address(0, 0)}
    catalog = [{"collection": 0, "title": "MASTER", "kind": "COLLECTION", "address": [0, 0]}]
    for name, title, kind in (
        ("delivery", "배달 목록", "LAYER"),
        ("coupang", "쿠팡", "WORLD"),
        ("baemin", "배민", "WORLD"),
        ("bridge", "위치 연결", "BRIDGE"),
        ("gps", "GPS", "WORLD"),
        ("references", "고정 위치 참조", "COLLECTION"),
    ):
        address = admin.collection(title, kind=kind)
        places[name] = address
        catalog.append({"collection": address.collection, "title": title, "kind": kind, "address": address.as_list()})

    positions = list(places.values())

    def add(board, title, target):
        address = admin.add(places[board].collection, title, target)
        positions.append(address)
        return address

    add("root", "배달 목록 열기", places["delivery"])
    add("root", "고정 위치 참조 열기", places["references"])
    first = add("delivery", "쿠팡으로 가는 칸", places["coupang"])
    add("delivery", "배민으로 가는 칸", places["baemin"])
    add("delivery", "위치 연결 열기", places["bridge"])
    add("delivery", "출발 목록으로", places["root"])
    add("coupang", "배달 목록으로", places["delivery"])
    add("baemin", "배달 목록으로", places["delivery"])
    add("bridge", "GPS 열기", places["gps"])
    add("gps", "배달 목록으로", places["delivery"])
    # This reference stays at 1:1 when the delivery list is reordered.
    add("references", "배달 목록의 1번 칸 참조", first)

    for name in ("coupang", "baemin"):
        admin.contract({
            "BASE_PIN": places["root"].text(),
            "COMMON_ACTION": "정산",
            "INNER_LENS": places[name].text(),
            "UNIQUE_ACTION": "일별 합계",
            "version": 1,
            "algorithm": "total",
            "input_type": "number_list",
        })

    bars, workspaces, workspace_entries, mix_targets = {}, {}, {}, {}
    for name in ("USER", "AI", "MASTER", "AGENT", "CODE"):
        key = admin.actor(name)
        for address in positions:
            admin.grant(key, address)
        bookmark = admin.bookmark(key, "목적지 책갈피", [places["coupang"], places["gps"], first])
        bars[name] = world.zoombar(key)
        workspace = admin.collection(f"{name} 혼합 작업판", owner_key=key)
        entry = admin.connect(0, workspace, f"{name} 혼합 작업판 열기")
        admin.connect(workspace.collection, places["root"], "출발 목록으로")
        # A destination bookmark remains non-traversable. This separate, explicit
        # real exit lets its owner navigate back into the existing network.
        admin.connect(bookmark.collection, places["root"], "출발 목록으로")
        workspaces[name] = workspace
        workspace_entries[name] = entry.slot
        mix_targets[name] = [
            {"title": "위치 BRIDGE 연결", "target": places["bridge"].as_list()},
            {"title": "배달 LAYER 연결", "target": places["delivery"].as_list()},
            {"title": "나의 BOOKMARK 연결", "target": bookmark.as_list()},
        ]
    return PositionDemo(world, bars, catalog, places, workspaces, workspace_entries, mix_targets)


def run_mixed_demo():
    demo = create_position_demo()
    try:
        bar = demo.bars['USER']
        bar.open(demo.workspace_entries['USER'], bar.view()['revision'])
        entries = [{'title': entry['title'], 'target': Address(*entry['target'])}
                   for entry in demo.mix_targets['USER']]
        slots = bar.mix(entries, bar.view()['revision'])
        first = slots[0]
        original = bar.view()['slots'][first.slot]
        bar.separate(first.slot, bar.view()['revision'])
        separated = bar.view()['slots'][first.slot]
        result = bar.reconnect(first.slot, bar.view()['revision'])
        restored = bar.view()['slots'][first.slot]
        visited = []
        for slot in slots:
            bar.open(slot.slot, bar.view()['revision'])
            visited.append({'address': bar.here().as_list(), 'kind': bar.view()['kind']})
            bar.out()
        return {
            'workspace': demo.workspaces['USER'].as_list(),
            'mixed_slots': [slot.as_list() for slot in slots],
            'visited_with_same_open': visited,
            'separate_kept_address': separated['address'] == original['address'],
            'separate_kept_target': separated['target'] == original['target'],
            'separated': separated['enabled'] is False,
            'reconnected_at_same_address': result == first and restored['address'] == original['address'],
            'restored': restored['enabled'] is True,
            'other_actor_still_at_root': demo.bars['AI'].path() == [Address(0)],
            'audit': demo.world.verify_history(),
        }
    finally:
        demo.world.close()


def run_position_demo():
    demo = create_position_demo()
    try:
        bar = demo.bars["USER"]
        code = demo.bars["CODE"]
        root = bar.view()
        bar.open(1, root["revision"])
        bar.open(1, bar.view()["revision"])
        parameter_hash = bar.put({
            "BASE_PIN": "0:0",
            "COMMON_ACTION": "정산",
            "INNER_LENS": demo.places["coupang"].text(),
            "UNIQUE_ACTION": "일별 합계",
            "data": [4500, 3800, 5200],
        })
        returned = bar.run(parameter_hash)
        result_hash = bar.last_result_hash()
        calculation = bar.read(result_hash)
        bar.root()
        bar.open(1, bar.view()["revision"])
        before = bar.view()
        old_slot = next(slot for slot in before["slots"] if slot["position"] == 1)
        bar.reorder(1, 2, before["revision"])
        after = bar.view()
        new_slot = next(slot for slot in after["slots"] if slot["position"] == 1)
        from .positional import PositionalError
        stale_rejected = False
        try:
            bar.open(1, before["revision"])
        except PositionalError as error:
            stale_rejected = error.code == "STALE_VIEW"
        bar.open(1, after["revision"])
        return {
            "identity": "collection_position:slot_position",
            "same_address": [demo.places["delivery"].collection, 1],
            "before": old_slot,
            "after": new_slot,
            "stale_selection_rejected": stale_rejected,
            "selected_target": bar.here().as_list(),
            "expected_new_target": demo.places["baemin"].as_list(),
            "code_path_unchanged": [a.as_list() for a in code.path()] == [[0, 0]],
            "calculation": calculation,
            "cycle_returned_none": returned is None,
            "parameter_hash": parameter_hash,
            "result_hash": result_hash,
            "zoombar_collection": bar.zoombar_view(),
            "bookmark_collections": bar.bookmarks(),
            "audit": demo.world.verify_history(),
        }
    finally:
        demo.world.close()
