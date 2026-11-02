"""Position is identity: executable contracts for the positional collection core.

These tests preserve the v0.1 test suite.  Coordinates remain fixed when board
contents move; this suite intentionally does not follow titles or hidden IDs.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from zoomconnect.positional import Address, PositionalError, PositionalWorld


def board_index(address):
    return address.as_list()[0]


def slot_index(address):
    return address.as_list()[1]


def at_slot(projection, position):
    return next(slot for slot in projection["slots"] if slot["position"] == position)


def open_slot(bar, address):
    """Select a fresh view's physical slot, never a title or stable identity."""
    projection = bar.view()
    bar.open(slot_index(address), projection["revision"])


class AddressContracts(unittest.TestCase):
    def test_address_is_the_collection_and_slot_coordinate(self):
        self.assertEqual(Address(3, 7).as_list(), [3, 7])
        self.assertEqual(Address(3, 7).text(), "3:7")
        self.assertEqual(Address(3).as_list(), [3, 0])

    def test_exporting_a_coordinate_does_not_expose_mutable_identity(self):
        address = Address(3, 7)
        exported = address.as_list()
        exported[1] = 99
        self.assertEqual(address.as_list(), [3, 7])


class PositionalContracts(unittest.TestCase):
    def setUp(self):
        self.world = PositionalWorld()
        self.master_key = self.world.setup()
        self.builder = self.world.admin(self.master_key)
        self.catalog = self.builder.collection("Catalog", kind="LAYER")
        self.a = self.builder.collection("A world", kind="COLLECTION")
        self.b = self.builder.collection("B world", kind="BRIDGE")
        self.catalog_slot_a = self.builder.add(board_index(self.catalog), "A", self.a)
        self.catalog_slot_b = self.builder.add(board_index(self.catalog), "B", self.b)
        self.root_catalog = self.builder.add(0, "Catalog", self.catalog)
        self.root_a = self.builder.add(0, "A world", self.a)
        self.root_b = self.builder.add(0, "B world", self.b)
        self.root_pinned = self.builder.add(0, "Pinned position", self.catalog_slot_a)
        self.a_catalog = self.builder.add(board_index(self.a), "Catalog", self.catalog)
        self.b_catalog = self.builder.add(board_index(self.b), "Catalog", self.catalog)
        self.alice_key = self.builder.actor("USER")
        self.bob_key = self.builder.actor("AI")
        addresses = (
            Address(0), self.catalog, self.a, self.b,
            self.catalog_slot_a, self.catalog_slot_b,
            self.root_catalog, self.root_a, self.root_b, self.root_pinned,
            self.a_catalog, self.b_catalog,
        )
        for key in (self.alice_key, self.bob_key):
            for address in addresses:
                self.builder.grant(key, address)
        self.alice = self.world.zoombar(self.alice_key)
        self.bob = self.world.zoombar(self.bob_key)

    def tearDown(self):
        self.world.close()

    def enter_catalog(self, bar=None):
        bar = self.alice if bar is None else bar
        bar.root()
        open_slot(bar, self.root_catalog)
        return bar

    def reorder_catalog(self):
        revision = self.enter_catalog().view()["revision"]
        self.builder.reorder(board_index(self.catalog), 1, 2, revision)

    def view_header(self, root_entry):
        self.alice.root()
        open_slot(self.alice, root_entry)
        return self.alice.view()

    def test_collection_header_and_item_positions_are_explicit(self):
        projection = self.enter_catalog().view()
        self.assertEqual(projection["collection"], board_index(self.catalog))
        self.assertEqual(at_slot(projection, 0)["address"], self.catalog.as_list())
        self.assertEqual(at_slot(projection, 1)["title"], "A")
        self.assertEqual(at_slot(projection, 2)["title"], "B")

    def test_reordering_contents_never_rewrites_an_existing_reference(self):
        original = at_slot(self.alice.view(), slot_index(self.root_pinned))["target"]
        self.assertEqual(original, self.catalog_slot_a.as_list())
        self.reorder_catalog()
        self.alice.root()
        refreshed = self.alice.view()
        self.assertEqual(at_slot(refreshed, slot_index(self.root_pinned))["target"], original)
        open_slot(self.alice, self.root_pinned)
        self.assertEqual(self.alice.here(), self.catalog_slot_a)
        self.assertEqual(self.alice.current()["title"], "B")

    def test_selection_after_refresh_uses_the_new_content_at_that_position(self):
        self.reorder_catalog()
        self.enter_catalog()
        self.assertEqual(at_slot(self.alice.view(), 1)["title"], "B")
        self.alice.open(1, self.alice.view()["revision"])
        self.assertEqual(self.alice.here(), self.b)

    def test_reference_resolution_is_exactly_one_hop(self):
        open_slot(self.alice, self.root_pinned)
        self.assertEqual(self.alice.here(), self.catalog_slot_a)
        self.assertNotEqual(self.alice.here(), self.a)
        self.assertEqual(self.alice.current()["target"], self.a.as_list())

    def test_old_view_cannot_select_rearranged_contents(self):
        old_revision = self.enter_catalog().view()["revision"]
        self.builder.reorder(board_index(self.catalog), 1, 2, old_revision)
        self.enter_catalog()
        with self.assertRaises(PositionalError) as failure:
            self.alice.open(1, old_revision)
        self.assertEqual(failure.exception.code, "STALE_VIEW")
        self.assertEqual(self.alice.here(), self.catalog)

    def test_replaced_target_requires_refresh_of_unchanged_incoming_reference(self):
        master = self.world.zoombar(self.master_key, session_id="target-change")

        def requires_refresh(entry, mutate, new_title):
            self.alice.root()
            before = self.alice.view()
            reference_before = at_slot(before, slot_index(entry))
            mutate()
            with self.assertRaises(PositionalError) as stale:
                self.alice.open(slot_index(entry), before["revision"])
            self.assertEqual(stale.exception.code, "STALE_VIEW")
            self.assertEqual(self.alice.here(), Address(0))
            after = self.alice.view()
            reference_after = at_slot(after, slot_index(entry))
            self.assertGreater(after["revision"], before["revision"])
            self.assertEqual(reference_after["address"], reference_before["address"])
            self.assertEqual(reference_after["target"], reference_before["target"])
            self.assertEqual(reference_after["revision"], reference_before["revision"])
            self.alice.open(slot_index(entry), after["revision"])
            self.assertEqual(self.alice.current()["title"], new_title)

        def reorder_target():
            master.root()
            open_slot(master, self.root_catalog)
            self.builder.reorder(board_index(self.catalog), 1, 2, master.view()["revision"])

        with self.subTest(change="target slot reordered"):
            requires_refresh(self.root_pinned, reorder_target, "B")

        def swap_target():
            master.root()
            open_slot(master, self.root_a)
            a_revision = master.view()["revision"]
            master.root()
            open_slot(master, self.root_b)
            b_revision = master.view()["revision"]
            self.builder.swap_collections(board_index(self.a), board_index(self.b), a_revision, b_revision)

        with self.subTest(change="target collection swapped"):
            requires_refresh(self.root_a, swap_target, "B world")

    def test_reorder_changes_the_revisions_of_affected_slots(self):
        before = self.enter_catalog().view()
        self.builder.reorder(board_index(self.catalog), 1, 2, before["revision"])
        after = self.enter_catalog().view()
        self.assertGreater(after["revision"], before["revision"])
        self.assertGreater(at_slot(after, 1)["revision"], at_slot(before, 1)["revision"])
        self.assertGreater(at_slot(after, 2)["revision"], at_slot(before, 2)["revision"])

    def test_a_stale_admin_reorder_is_not_silently_applied(self):
        old_revision = self.enter_catalog().view()["revision"]
        self.builder.reorder(board_index(self.catalog), 1, 2, old_revision)
        with self.assertRaises(PositionalError) as failure:
            self.builder.reorder(board_index(self.catalog), 1, 2, old_revision)
        self.assertEqual(failure.exception.code, "STALE_VIEW")
        self.assertEqual(at_slot(self.enter_catalog().view(), 1)["title"], "B")

    def test_removing_a_slot_leaves_a_tombstone_and_does_not_shift_neighbors(self):
        before = self.enter_catalog().view()
        self.builder.remove(board_index(self.catalog), 1, before["revision"])
        after = self.enter_catalog().view()
        self.assertTrue(at_slot(after, 1)["empty"])
        self.assertEqual(at_slot(after, 2)["title"], "B")
        self.assertEqual(at_slot(after, 2)["address"], self.catalog_slot_b.as_list())

    def test_new_items_append_without_reusing_a_deleted_identity(self):
        revision = self.enter_catalog().view()["revision"]
        self.builder.remove(board_index(self.catalog), 1, revision)
        added = self.builder.add(board_index(self.catalog), "C", self.a)
        self.assertEqual(added, Address(board_index(self.catalog), 3))
        projection = self.enter_catalog().view()
        self.assertTrue(at_slot(projection, 1)["empty"])
        self.assertEqual(at_slot(projection, 3)["title"], "C")

    def test_selecting_an_empty_slot_is_rejected(self):
        revision = self.enter_catalog().view()["revision"]
        self.builder.remove(board_index(self.catalog), 1, revision)
        projection = self.enter_catalog().view()
        with self.assertRaises(PositionalError) as failure:
            self.alice.open(1, projection["revision"])
        self.assertEqual(failure.exception.code, "EMPTY_SLOT")

    def test_a_reference_to_a_deleted_target_does_not_fall_through_to_the_next_item(self):
        revision = self.enter_catalog().view()["revision"]
        self.builder.remove(board_index(self.catalog), 1, revision)
        self.alice.root()
        with self.assertRaises(PositionalError) as failure:
            open_slot(self.alice, self.root_pinned)
        self.assertEqual(failure.exception.code, "EMPTY_TARGET")
        self.assertEqual(self.alice.here(), Address(0))

    def test_collection_header_cannot_be_deleted_or_moved_as_an_item(self):
        revision = self.enter_catalog().view()["revision"]
        with self.assertRaises(PositionalError):
            self.builder.remove(board_index(self.catalog), 0, revision)
        with self.assertRaises(PositionalError):
            self.builder.reorder(board_index(self.catalog), 0, 1, revision)

    def test_root_header_is_protected(self):
        projection = self.alice.view()
        with self.assertRaises(PositionalError):
            self.builder.remove(0, 0, projection["revision"])
        self.assertEqual(self.alice.here(), Address(0))

    def test_disabled_position_cannot_be_used_as_a_connection(self):
        revision = self.enter_catalog().view()["revision"]
        self.builder.switch(board_index(self.catalog), 1, False, revision)
        projection = self.enter_catalog().view()
        self.assertFalse(at_slot(projection, 1)["enabled"])
        with self.assertRaises(PositionalError):
            self.alice.open(1, projection["revision"])

    def test_visited_target_rearrangement_requires_safe_return(self):
        open_slot(self.alice, self.root_pinned)
        self.assertEqual(self.alice.here(), self.catalog_slot_a)
        master = self.world.zoombar(self.master_key)
        open_slot(master, self.root_catalog)
        self.builder.reorder(board_index(self.catalog), 1, 2, master.view()["revision"])
        with self.assertRaises(PositionalError) as failure:
            self.alice.current()
        self.assertEqual(failure.exception.code, "STALE_PATH")
        self.assertEqual(self.alice.out(), "SAFE_RETURN")
        self.assertEqual(self.alice.here(), Address(0))

    def test_visited_via_position_rearrangement_invalidates_the_old_path(self):
        self.enter_catalog()
        self.alice.open(1, self.alice.view()["revision"])
        master = self.world.zoombar(self.master_key)
        open_slot(master, self.root_catalog)
        self.builder.reorder(board_index(self.catalog), 1, 2, master.view()["revision"])
        self.assertEqual(self.alice.out(), "SAFE_RETURN")
        self.assertNotEqual(self.alice.here(), self.a)

    def test_visit_history_returns_along_a_one_way_connection(self):
        self.enter_catalog()
        self.alice.open(1, self.alice.view()["revision"])
        self.assertEqual(self.alice.here(), self.a)
        self.assertEqual(self.alice.out(), "ENTRY")
        self.assertEqual(self.alice.here(), self.catalog)
        self.assertEqual(self.alice.out(), "ENTRY")
        self.assertEqual(self.alice.here(), Address(0))

    def test_repeated_visits_are_distinct_history_frames(self):
        self.enter_catalog()
        self.alice.open(1, self.alice.view()["revision"])
        open_slot(self.alice, self.a_catalog)
        self.alice.open(1, self.alice.view()["revision"])
        self.assertEqual(self.alice.path().count(self.a), 2)
        self.assertEqual(self.alice.path().count(self.catalog), 2)

    def test_zoom_out_keeps_history_slots_instead_of_reindexing_them(self):
        before = len(self.alice.zoombar_view()["slots"])
        self.enter_catalog()
        self.alice.open(1, self.alice.view()["revision"])
        entered = self.alice.zoombar_view()
        entered_addresses = [slot["address"] for slot in entered["slots"]]
        self.assertGreaterEqual(len(entered_addresses), before + 2)
        self.alice.out()
        after = self.alice.zoombar_view()
        self.assertEqual([slot["address"] for slot in after["slots"]], entered_addresses)
        self.assertEqual(self.alice.path(), [Address(0), self.catalog])

    def test_actors_and_sessions_have_independent_positions(self):
        self.enter_catalog()
        self.assertEqual(self.bob.path(), [Address(0)])
        another = self.world.zoombar(self.alice_key, session_id="separate-view")
        self.assertEqual(another.path(), [Address(0)])
        self.assertEqual(self.alice.here(), self.catalog)

    def test_a_known_session_identifier_is_not_an_authentication_credential(self):
        owner = self.world.zoombar(self.alice_key, session_id="owner-view")
        self.enter_catalog(owner)
        other = self.world.zoombar(self.bob_key, session_id="owner-view")
        self.assertEqual(other.path(), [Address(0)])
        self.assertEqual(owner.here(), self.catalog)
        self.assertNotEqual(owner.identity()["zoombar_address"], other.identity()["zoombar_address"])
        with self.assertRaises(PositionalError):
            self.world.zoombar("not-a-valid-key", session_id="owner-view")

    def test_same_actor_display_names_and_local_session_names_do_not_mix_histories(self):
        first_key = self.builder.actor("DUPLICATE_DISPLAY_NAME")
        second_key = self.builder.actor("DUPLICATE_DISPLAY_NAME")
        for key in (first_key, second_key):
            for address in (Address(0), self.root_catalog, self.catalog, self.root_b, self.b):
                self.builder.grant(key, address)
        first = self.world.zoombar(first_key, session_id="default")
        second = self.world.zoombar(second_key, session_id="default")
        self.assertEqual(first.identity()["name"], second.identity()["name"])
        self.assertEqual(first.identity()["session_id"], second.identity()["session_id"])
        self.assertNotEqual(first.identity()["zoombar_address"], second.identity()["zoombar_address"])
        open_slot(first, self.root_catalog)
        first_history = first.history(500)
        self.assertTrue(first_history)
        self.assertEqual(second.history(500), [])
        open_slot(second, self.root_b)
        self.assertEqual(first.history(500), first_history)
        self.assertEqual(first.here(), self.catalog)
        self.assertEqual(second.here(), self.b)
        first_sequences = {event["sequence"] for event in first_history}
        second_sequences = {event["sequence"] for event in second.history(500)}
        self.assertTrue(second_sequences)
        self.assertFalse(first_sequences & second_sequences)

    def test_item_write_permission_does_not_authorize_editing_other_board_positions(self):
        board = self.builder.collection("Restricted board", kind="LAYER")
        entry = self.builder.add(board_index(board), "Entry", self.a)
        self.builder.add(board_index(board), "B", self.b)
        self.builder.add(board_index(board), "C", self.catalog)
        root_entry = self.builder.add(0, "Restricted entry", entry)
        key = self.builder.actor("POSITION_WRITER")
        self.builder.grant(key, root_entry, rights=("move", "read"))
        self.builder.grant(key, board, rights=("move", "read"))
        self.builder.grant(key, entry, rights=("move", "read", "write"))
        bar = self.world.zoombar(key)
        open_slot(bar, root_entry)
        self.assertEqual(bar.here(), entry)
        bar.put({"current position only": True})
        before = bar.view()
        operations = (
            lambda: bar.reorder(2, 3, before["revision"]),
            lambda: bar.remove(2, before["revision"]),
            lambda: bar.switch(2, False, before["revision"]),
        )
        for operation in operations:
            with self.assertRaises(PositionalError) as failure:
                operation()
            self.assertEqual(failure.exception.code, "RIGHTS_DENIED")
            self.assertEqual(bar.view(), before)

        self.builder.grant(key, board, rights=("write",))
        bar.reorder(2, 3, bar.view()["revision"])
        self.assertEqual(at_slot(bar.view(), 2)["title"], "C")
        self.assertEqual(at_slot(bar.view(), 3)["title"], "B")
        bar.switch(2, False, bar.view()["revision"])
        self.assertFalse(at_slot(bar.view(), 2)["enabled"])
        bar.remove(3, bar.view()["revision"])
        self.assertTrue(at_slot(bar.view(), 3)["empty"])

    def test_user_cannot_obtain_the_master_configuration_handle(self):
        with self.assertRaises(PositionalError):
            self.world.admin(self.alice_key)

    def test_an_arbitrary_new_kind_does_not_require_an_engine_registration(self):
        new = self.builder.collection("New connected world", kind="A_NEW_KIND")
        entry = self.builder.add(0, "New connected world", new)
        self.builder.grant(self.alice_key, new)
        self.builder.grant(self.alice_key, entry)
        self.alice.root()
        open_slot(self.alice, entry)
        self.assertEqual(self.alice.here(), new)
        self.assertEqual(self.alice.view()["kind"], "A_NEW_KIND")

    def test_collection_projections_have_coordinates_without_hidden_lens_uids(self):
        projections = [self.alice.view(), self.enter_catalog().view(), self.alice.zoombar_view()]
        for projection in projections:
            with self.subTest(kind=projection["kind"]):
                self.assertTrue({"collection", "revision", "title", "kind", "slots"} <= projection.keys())
                self.assertFalse({"uid", "uuid", "lens_id"} & projection.keys())
                for record in projection["slots"]:
                    self.assertEqual(record["address"], [projection["collection"], record["position"]])
                    self.assertFalse({"uid", "uuid", "lens_id"} & record.keys())

    def test_bookmarks_are_common_collections_of_coordinate_references(self):
        bookmark = self.builder.bookmark(self.alice_key, "Favorites", [self.a, self.b])
        projections = self.alice.bookmarks()
        projection = next(item for item in projections if item["collection"] == board_index(bookmark))
        self.assertEqual(projection["kind"], "BOOKMARK")
        self.assertEqual(at_slot(projection, 1)["target"], self.a.as_list())
        self.assertFalse(at_slot(projection, 1)["traversable"])
        self.assertEqual(at_slot(projection, 2)["target"], self.b.as_list())

    def test_bookmark_collections_are_private_to_their_owner(self):
        bookmark = self.builder.bookmark(self.alice_key, "Private favorites", [self.a])
        self.assertIn(board_index(bookmark), [board["collection"] for board in self.alice.bookmarks()])
        self.assertNotIn(board_index(bookmark), [board["collection"] for board in self.bob.bookmarks()])

    def test_old_bookmark_view_cannot_select_a_reordered_destination(self):
        bookmark = self.builder.bookmark(self.alice_key, "Favorites", [self.a, self.b])
        projection = next(item for item in self.alice.bookmarks() if item["collection"] == board_index(bookmark))
        old_revision = projection["revision"]
        self.builder.reorder(board_index(bookmark), 1, 2, old_revision)
        with self.assertRaises(PositionalError) as failure:
            self.alice.bookmark(board_index(bookmark), 1, old_revision)
        self.assertEqual(failure.exception.code, "STALE_VIEW")
        self.assertEqual(self.alice.here(), Address(0))

    def test_bookmark_navigation_walks_real_connections(self):
        bookmark = self.builder.bookmark(self.alice_key, "Favorites", [self.b])
        projection = next(item for item in self.alice.bookmarks() if item["collection"] == board_index(bookmark))
        self.alice.bookmark(board_index(bookmark), 1, projection["revision"])
        path = self.alice.path()
        self.assertEqual(path[0], Address(0))
        self.assertEqual(path[-1], self.b)
        self.assertGreaterEqual(len(path), 2)
        self.assertNotIn(bookmark, path)

    def test_bookmark_reference_does_not_grant_access_to_a_private_position(self):
        private = self.builder.collection("Private")
        self.builder.add(0, "Private route", private)
        bookmark = self.builder.bookmark(self.alice_key, "Private target", [private])
        projection = next(item for item in self.alice.bookmarks() if item["collection"] == board_index(bookmark))
        with self.assertRaises(PositionalError):
            self.alice.bookmark(board_index(bookmark), 1, projection["revision"])
        self.assertEqual(self.alice.here(), Address(0))

    def test_url_is_a_sequence_of_current_board_slot_choices(self):
        url = "zoom://world/0:0/" + str(slot_index(self.root_catalog)) + "/1"
        self.alice.walk(url)
        self.assertEqual(self.alice.path(), [Address(0), self.catalog, self.a])

    def test_url_does_not_use_a_remote_address_as_a_teleport(self):
        with self.assertRaises(PositionalError):
            self.alice.walk("zoom://world/" + self.b.text())
        self.assertEqual(self.alice.here(), Address(0))

    def test_nonexistent_position_is_rejected_without_moving(self):
        revision = self.alice.view()["revision"]
        with self.assertRaises(PositionalError):
            self.alice.open(999_999, revision)
        self.assertEqual(self.alice.path(), [Address(0)])

    def test_a_revision_from_another_board_cannot_authorize_current_board_selection(self):
        root_revision = self.alice.view()["revision"]
        self.enter_catalog()
        with self.assertRaises(PositionalError) as failure:
            self.alice.open(1, root_revision)
        self.assertEqual(failure.exception.code, "STALE_VIEW")
        self.assertEqual(self.alice.here(), self.catalog)

    def test_data_hash_is_a_snapshot_not_a_live_object_reference(self):
        self.enter_catalog()
        data = {"days": [[1, 2], [3]], "note": "비 옴"}
        reference = self.alice.put(data)
        data["days"][0].append(99)
        self.assertEqual(self.alice.read(reference), {"days": [[1, 2], [3]], "note": "비 옴"})
        returned = self.alice.read(reference)
        returned["days"].clear()
        self.assertEqual(self.alice.read(reference)["days"], [[1, 2], [3]])

    def test_data_hash_is_scoped_to_the_current_coordinate(self):
        self.enter_catalog()
        reference = self.alice.put({"value": 7})
        self.alice.open(1, self.alice.view()["revision"])
        with self.assertRaises(PositionalError):
            self.alice.read(reference)

    def test_replaced_position_does_not_inherit_the_previous_occupants_data_hash(self):
        open_slot(self.alice, self.root_pinned)
        reference = self.alice.put({"A-private": 7})
        master = self.world.zoombar(self.master_key)
        open_slot(master, self.root_catalog)
        self.builder.reorder(board_index(self.catalog), 1, 2, master.view()["revision"])
        self.alice.root()
        open_slot(self.alice, self.root_pinned)
        self.assertEqual(self.alice.current()["title"], "B")
        with self.assertRaises(PositionalError) as failure:
            self.alice.read(reference)
        self.assertEqual(failure.exception.code, "FOREIGN_OR_STALE_HASH")

    def test_read_only_access_does_not_authorize_data_mutation(self):
        key = self.builder.actor("READ_ONLY")
        bar = self.world.zoombar(key)
        self.assertEqual(bar.here(), Address(0))
        with self.assertRaises(PositionalError):
            bar.put({"changed": True})

    def test_history_remains_verifiable_after_real_navigation_and_reordering(self):
        self.enter_catalog()
        self.alice.open(1, self.alice.view()["revision"])
        self.alice.out()
        self.reorder_catalog()
        self.alice.root()
        report = self.world.verify_history()
        self.assertTrue(report["valid"])
        self.assertGreater(report["events"], 0)

    def test_global_collection_swap_preserves_reference_and_permission_coordinates(self):
        key = self.builder.actor("ONLY_OLD_A_POSITION")
        self.builder.grant(key, self.root_a, rights=("move", "read"))
        self.builder.grant(key, self.a)
        restricted = self.world.zoombar(key)
        before_b = self.view_header(self.root_b)
        before_a = self.view_header(self.root_a)
        self.builder.swap_collections(
            board_index(self.a), board_index(self.b), before_a["revision"], before_b["revision"]
        )
        with self.assertRaises(PositionalError) as stale:
            self.alice.current()
        self.assertEqual(stale.exception.code, "STALE_PATH")
        self.assertEqual(self.alice.out(), "SAFE_RETURN")
        self.assertEqual(self.alice.here(), Address(0))
        root = self.alice.view()
        self.assertEqual(at_slot(root, slot_index(self.root_a))["target"], self.a.as_list())
        self.assertEqual(at_slot(root, slot_index(self.root_b))["target"], self.b.as_list())
        open_slot(restricted, self.root_a)
        self.assertEqual(restricted.here(), self.a)
        self.assertEqual(restricted.current()["title"], "B world")
        after_a = restricted.view()
        self.assertEqual(at_slot(after_a, 0)["revision"], at_slot(before_a, 0)["revision"] + 1)
        restricted.root()
        with self.assertRaises(PositionalError):
            open_slot(restricted, self.root_b)
        after_b = self.view_header(self.root_b)
        self.assertEqual(after_b["title"], "A world")
        self.assertEqual(at_slot(after_b, 0)["revision"], at_slot(before_b, 0)["revision"] + 1)

    def test_global_swap_leaves_tombstones_when_the_incoming_collection_is_shorter(self):
        extra = self.builder.add(board_index(self.a), "Extra item", self.catalog)
        before_a = self.view_header(self.root_a)
        before_b = self.view_header(self.root_b)
        self.builder.swap_collections(
            board_index(self.a), board_index(self.b), before_a["revision"], before_b["revision"]
        )
        after_a = self.view_header(self.root_a)
        after_b = self.view_header(self.root_b)
        self.assertTrue(at_slot(after_a, slot_index(extra))["empty"])
        self.assertEqual(at_slot(after_a, slot_index(extra))["address"], extra.as_list())
        self.assertEqual(at_slot(after_a, slot_index(extra))["revision"], at_slot(before_a, slot_index(extra))["revision"] + 1)
        self.assertEqual(at_slot(after_b, slot_index(extra))["title"], "Extra item")
        self.assertEqual(at_slot(after_b, slot_index(extra))["address"], [board_index(self.b), slot_index(extra)])
        self.assertEqual(at_slot(after_b, slot_index(extra))["target"], self.catalog.as_list())

    def test_global_swap_protects_root_actor_roots_and_private_runtime_collections(self):
        root_revision = self.alice.view()["revision"]
        before_a = self.view_header(self.root_a)
        with self.assertRaises(PositionalError) as root_failure:
            self.builder.swap_collections(0, board_index(self.a), root_revision, before_a["revision"])
        self.assertEqual(root_failure.exception.code, "ROOT_COLLECTION")
        private = self.alice.zoombar_view()
        with self.assertRaises(PositionalError) as private_failure:
            self.builder.swap_collections(private["collection"], board_index(self.a), private["revision"], before_a["revision"])
        self.assertEqual(private_failure.exception.code, "PROTECTED_COLLECTION")
        self.builder.actor("CUSTOM_ROOT", root=self.a)
        before_b = self.view_header(self.root_b)
        with self.assertRaises(PositionalError) as actor_root_failure:
            self.builder.swap_collections(board_index(self.a), board_index(self.b), before_a["revision"], before_b["revision"])
        self.assertEqual(actor_root_failure.exception.code, "ROOT_COLLECTION")

    def positional_binding(self, base_pin=None):
        return {
            "BASE_PIN": Address(0).text() if base_pin is None else base_pin,
            "COMMON_ACTION": "정산", "INNER_LENS": self.a.text(),
            "UNIQUE_ACTION": "합", "algorithm": "total", "version": 1,
        }

    def positional_request(self, data, base_pin=None):
        return {
            "BASE_PIN": Address(0).text() if base_pin is None else base_pin,
            "COMMON_ACTION": "정산", "INNER_LENS": self.a.text(),
            "UNIQUE_ACTION": "합", "data": data,
        }

    def test_positional_execution_uses_one_hash_and_records_result_without_returning_it(self):
        self.builder.contract(self.positional_binding())
        self.view_header(self.root_a)
        parameter = self.alice.put(self.positional_request([4500, 3800, 5200]))
        self.assertIsNone(self.alice.run(parameter))
        result_hash = self.alice.last_result_hash()
        self.assertTrue(result_hash.startswith("pos1:"))
        result = self.alice.read(result_hash)
        self.assertEqual(result["result"], 13_500)
        self.assertEqual(result["parameter_hash"], parameter)
        done = next(event for event in self.alice.history(500) if event["kind"] == "CYCLE_DONE")
        self.assertEqual(done["body"]["result_hash"], result_hash)
        self.assertEqual(self.alice.path(), [Address(0), self.a])
        self.assertTrue(self.world.verify_history()["valid"])

    def test_old_parameter_and_contract_cannot_execute_a_new_occupant_after_swap(self):
        self.builder.contract(self.positional_binding())
        before_b = self.view_header(self.root_b)
        before_a = self.view_header(self.root_a)
        old_parameter = self.alice.put(self.positional_request([1, 2]))
        self.builder.swap_collections(board_index(self.a), board_index(self.b), before_a["revision"], before_b["revision"])
        self.alice.out()
        open_slot(self.alice, self.root_a)
        self.assertEqual(self.alice.current()["title"], "B world")
        with self.assertRaises(PositionalError) as stale_hash:
            self.alice.run(old_parameter)
        self.assertEqual(stale_hash.exception.code, "FOREIGN_OR_STALE_HASH")
        fresh_parameter = self.alice.put(self.positional_request([1, 2]))
        with self.assertRaises(PositionalError) as stale_contract:
            self.alice.run(fresh_parameter)
        self.assertEqual(stale_contract.exception.code, "STALE_CONTRACT")
        self.assertNotIn("CYCLE_DONE", [event["kind"] for event in self.alice.history(500)])

    def test_execution_requires_result_write_permission_and_an_actually_visited_base_pin(self):
        self.builder.contract(self.positional_binding())
        self.view_header(self.root_a)
        parameter = self.alice.put(self.positional_request([1, 2, 3]))
        key = self.builder.actor("EXECUTE_WITHOUT_WRITE")
        self.builder.grant(key, self.root_a, rights=("move", "read"))
        self.builder.grant(key, self.a, rights=("move", "read", "execute"))
        bar = self.world.zoombar(key)
        open_slot(bar, self.root_a)
        with self.assertRaises(PositionalError) as denied:
            bar.run(parameter)
        self.assertEqual(denied.exception.code, "RIGHTS_DENIED")
        self.builder.grant(key, self.a, rights=("write",))
        self.assertIsNone(bar.run(parameter))
        self.assertEqual(bar.read(bar.last_result_hash())["result"], 6)
        self.builder.contract(self.positional_binding(base_pin=self.catalog.text()))
        invalid_base = bar.put(self.positional_request([1, 2, 3], base_pin=self.catalog.text()))
        with self.assertRaises(PositionalError) as missing_path:
            bar.run(invalid_base)
        self.assertEqual(missing_path.exception.code, "BASE_PIN_NOT_IN_PATH")


class PositionalPersistenceContracts(unittest.TestCase):
    def tamper(self, statements):
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "tampered-positions.sqlite")
            world = PositionalWorld(database)
            master_key = world.setup()
            world.admin(master_key).collection("A")
            self.assertTrue(world.verify_history()["valid"])
            world.close()
            with sqlite3.connect(database) as connection:
                connection.execute("DROP TRIGGER positional_events_no_update")
                connection.execute("DROP TRIGGER positional_events_no_delete")
                for statement, parameters in statements:
                    connection.execute(statement, parameters)
            reopened = PositionalWorld(database)
            try:
                self.assertFalse(reopened.verify_history()["valid"])
            finally:
                reopened.close()

    def test_changed_history_payload_is_detected(self):
        self.tamper([("UPDATE positional_events SET body=? WHERE sequence=1", ('{"forged":true}',))])

    def test_malformed_history_payload_is_reported_as_invalid(self):
        self.tamper([("UPDATE positional_events SET body=? WHERE sequence=1", ("not-json",))])

    def test_removed_history_tail_is_detected(self):
        self.tamper([("DELETE FROM positional_events WHERE sequence=(SELECT MAX(sequence) FROM positional_events)", ())])

    def test_removed_entire_history_is_detected(self):
        self.tamper([("DELETE FROM positional_events", ())])

    def test_history_is_append_only_under_ordinary_sql(self):
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "immutable-positions.sqlite")
            world = PositionalWorld(database)
            world.setup()
            world.close()
            with sqlite3.connect(database) as connection:
                for statement in ("UPDATE positional_events SET kind='forged'", "DELETE FROM positional_events"):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(statement)

    def test_out_of_band_board_content_changes_are_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "state-tamper.sqlite")
            world = PositionalWorld(database)
            world.setup()
            world.close()
            with sqlite3.connect(database) as connection:
                state = json.loads(connection.execute("SELECT body FROM positional_state WHERE singleton=1").fetchone()[0])
                # Change valid JSON without changing the independent history anchor.
                state["unapproved_change"] = True
                connection.execute("UPDATE positional_state SET body=? WHERE singleton=1", (json.dumps(state),))
            reopened = PositionalWorld(database)
            try:
                self.assertFalse(reopened.verify_history()["valid"])
            finally:
                reopened.close()

    def test_multiple_world_connections_allocate_distinct_positions_and_one_audit_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "shared-positions.sqlite")
            world = PositionalWorld(database)
            master_key = world.setup()
            world.close()

            def allocate(worker):
                worker_world = PositionalWorld(database)
                try:
                    builder = worker_world.admin(master_key)
                    return [builder.collection("worker " + str(worker) + " board " + str(index)) for index in range(8)]
                finally:
                    worker_world.close()

            with ThreadPoolExecutor(max_workers=4) as pool:
                groups = list(pool.map(allocate, range(4)))
            positions = [tuple(address.as_list()) for group in groups for address in group]
            self.assertEqual(len(positions), 32)
            self.assertEqual(len(set(positions)), 32)
            self.assertTrue(all(slot == 0 for collection, slot in positions))
            reopened = PositionalWorld(database)
            try:
                self.assertTrue(reopened.verify_history()["valid"])
                self.assertGreater(reopened.verify_history()["events"], 32)
            finally:
                reopened.close()

    def test_restart_preserves_fixed_coordinates_rearranged_contents_and_private_path(self):
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "positions.sqlite")
            world = PositionalWorld(database)
            master_key = world.setup()
            builder = world.admin(master_key)
            board = builder.collection("Board", kind="LAYER")
            a = builder.collection("A")
            b = builder.collection("B")
            first = builder.add(board_index(board), "A", a)
            second = builder.add(board_index(board), "B", b)
            root_entry = builder.add(0, "Board", board)
            fixed_reference = builder.add(0, "Fixed", first)
            key = builder.actor("CODE")
            for address in (Address(0), board, a, b, first, second, root_entry, fixed_reference):
                builder.grant(key, address)
            bar = world.zoombar(key, session_id="saved-position")
            open_slot(bar, root_entry)
            builder.reorder(board_index(board), 1, 2, bar.view()["revision"])
            bar.root()
            open_slot(bar, fixed_reference)
            self.assertEqual(bar.current()["title"], "B")
            event_count = world.verify_history()["events"]
            world.close()
            reopened = PositionalWorld(database)
            try:
                restored = reopened.zoombar(key, session_id="saved-position")
                self.assertEqual(restored.here(), first)
                self.assertEqual(restored.current()["title"], "B")
                self.assertEqual(restored.current()["target"], b.as_list())
                self.assertEqual(restored.path(), [Address(0), first])
                self.assertTrue(reopened.verify_history()["valid"])
                self.assertGreaterEqual(reopened.verify_history()["events"], event_count)
                self.assertIsNotNone(reopened.admin(master_key))
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
