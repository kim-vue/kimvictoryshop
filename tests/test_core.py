"""Observable contracts, not copies of the engine's navigation algorithm.

All credentials in these tests are generated for disposable databases.  No
third-party binaries, services, or user files are executed or modified.
"""

from __future__ import annotations

import ast
from concurrent.futures import ThreadPoolExecutor
import inspect
from pathlib import Path
import sqlite3
import tempfile
import unittest
from urllib.parse import quote

from zoomconnect import core
from zoomconnect.core import World, ZoomError, Zoombar
from zoomconnect.execution import ExecutionError


class NavigationContracts(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.master_key = self.world.setup()
        self.builder = self.world.admin(self.master_key)
        for uid, kind in (
            ("BRIDGE_1", "BRIDGE"),
            ("A", "LENS"),
            ("LAYER_1", "LAYER"),
            ("B", "LENS"),
            ("PRIVATE", "LENS"),
        ):
            self.builder.lens(uid, label=uid, kind=kind)
        self.edges = [
            self.builder.connect("MASTER", "BRIDGE_1", connection_id="root_bridge"),
            self.builder.connect("BRIDGE_1", "A", connection_id="bridge_a"),
            self.builder.connect("A", "LAYER_1", connection_id="a_layer"),
            self.builder.connect("LAYER_1", "B", connection_id="layer_b"),
        ]
        self.builder.connect("MASTER", "PRIVATE", connection_id="private_edge")
        self.alice_key = self.builder.actor("USER")
        self.bob_key = self.builder.actor("AI")
        for key in (self.alice_key, self.bob_key):
            for uid in ("MASTER", "BRIDGE_1", "A", "LAYER_1", "B"):
                self.builder.grant(key, uid)
        self.alice = self.world.zoombar(self.alice_key)
        self.bob = self.world.zoombar(self.bob_key)

    def tearDown(self):
        self.world.close()

    def enter_a(self, bar=None):
        bar = self.alice if bar is None else bar
        bar.zoom_in("BRIDGE_1")
        bar.zoom_in("A")
        return bar

    def enter_b(self, bar=None):
        bar = self.enter_a(bar)
        bar.zoom_in("LAYER_1")
        bar.zoom_in("B")
        return bar

    def test_only_authorized_immediate_connections_are_visible(self):
        self.assertEqual([entry["uid"] for entry in self.alice.see()], ["BRIDGE_1"])
        self.assertEqual(self.alice.here(), "MASTER")

    def test_known_uid_does_not_allow_a_jump(self):
        before = self.alice.path()
        with self.assertRaises(ZoomError):
            self.alice.zoom_in("B")
        self.assertEqual(self.alice.path(), before)

    def test_an_existing_connection_without_permission_is_not_traversable(self):
        with self.assertRaises(ZoomError):
            self.alice.zoom_in("PRIVATE")
        self.assertEqual(self.alice.here(), "MASTER")

    def test_bridge_and_layer_use_the_same_sequence_of_moves(self):
        self.enter_b()
        self.assertEqual(
            self.alice.path(), ["MASTER", "BRIDGE_1", "A", "LAYER_1", "B"]
        )

    def test_a_previously_unknown_kind_needs_no_new_engine_case(self):
        self.builder.lens("NEW", label="A new world", kind="NEVER_REGISTERED_KIND")
        self.builder.connect("B", "NEW")
        self.builder.grant(self.alice_key, "NEW")
        self.enter_b()
        self.assertEqual(self.alice.see()[0]["kind"], "NEVER_REGISTERED_KIND")
        self.alice.zoom_in("NEW")
        self.assertEqual(self.alice.here(), "NEW")
        self.assertEqual(self.alice.zoom_out(), "ENTRY")
        self.assertEqual(self.alice.here(), "B")

    def test_directed_connection_does_not_create_a_reverse_entry(self):
        self.enter_a()
        self.assertNotIn("BRIDGE_1", [entry["uid"] for entry in self.alice.see()])
        with self.assertRaises(ZoomError):
            self.alice.zoom_in("BRIDGE_1")

    def test_return_uses_real_visit_history_even_on_a_directed_connection(self):
        self.enter_a()
        self.assertEqual(self.alice.zoom_out(), "ENTRY")
        self.assertEqual(self.alice.path(), ["MASTER", "BRIDGE_1"])
        self.assertEqual(self.alice.zoom_out(), "ENTRY")
        self.assertEqual(self.alice.path(), ["MASTER"])
        self.assertEqual(self.alice.zoom_out(), "ROOT")

    def test_revisiting_a_world_preserves_each_visit(self):
        self.builder.connect("B", "A")
        self.enter_b()
        self.alice.zoom_in("A")
        self.assertEqual(self.alice.path().count("A"), 2)
        self.alice.zoom_out()
        self.assertEqual(self.alice.path(), ["MASTER", "BRIDGE_1", "A", "LAYER_1", "B"])

    def test_disconnect_of_entry_returns_to_the_last_connected_prefix(self):
        self.enter_b()
        self.builder.disconnect("layer_b")
        self.assertEqual(self.alice.zoom_out(), "SAFE_RETURN")
        self.assertEqual(self.alice.path(), ["MASTER", "BRIDGE_1", "A", "LAYER_1"])

    def test_disconnect_of_an_ancestor_does_not_leave_a_detached_path(self):
        self.enter_b()
        self.builder.disconnect("root_bridge")
        self.assertEqual(self.alice.zoom_out(), "SAFE_RETURN")
        self.assertEqual(self.alice.path(), ["MASTER"])

    def test_parallel_connection_can_be_selected_explicitly(self):
        second = self.builder.connect("MASTER", "BRIDGE_1", connection_id="root_bridge_2")
        self.alice.zoom_in("BRIDGE_1", connection_id=second)
        self.builder.disconnect("root_bridge")
        self.assertEqual(self.alice.zoom_out(), "ENTRY")
        self.assertEqual(self.alice.here(), "MASTER")

    def test_an_unrelated_connection_id_cannot_authorize_a_move(self):
        with self.assertRaises(ZoomError):
            self.alice.zoom_in("BRIDGE_1", connection_id="layer_b")
        self.assertEqual(self.alice.path(), ["MASTER"])

    def test_disconnect_is_local_to_that_connection(self):
        extra = self.builder.connect("MASTER", "BRIDGE_1", connection_id="other_route")
        self.builder.disconnect("root_bridge")
        self.alice.zoom_in("BRIDGE_1", connection_id=extra)
        self.alice.zoom_in("A")
        self.assertEqual(self.alice.here(), "A")

    def test_each_actor_keeps_its_own_position(self):
        self.enter_b()
        self.assertEqual(self.bob.path(), ["MASTER"])
        self.bob.zoom_in("BRIDGE_1")
        self.assertEqual(self.alice.here(), "B")

    def test_two_sessions_for_the_same_actor_are_independent(self):
        left = self.world.zoombar(self.alice_key, session_id="left-view")
        right = self.world.zoombar(self.alice_key, session_id="right-view")
        left.zoom_in("BRIDGE_1")
        self.assertEqual(right.path(), ["MASTER"])
        self.assertEqual(left.path(), ["MASTER", "BRIDGE_1"])

    def test_own_session_can_be_resumed(self):
        bar = self.world.zoombar(self.alice_key, session_id="resumable")
        self.enter_a(bar)
        resumed = self.world.zoombar(self.alice_key, session_id=bar.session_id)
        self.assertEqual(resumed.path(), ["MASTER", "BRIDGE_1", "A"])

    def test_stolen_session_id_does_not_authenticate_another_actor(self):
        self.enter_a()
        with self.assertRaises(ZoomError):
            self.world.zoombar(self.bob_key, session_id=self.alice.session_id)
        self.assertEqual(self.alice.here(), "A")

    def test_unknown_credential_is_rejected(self):
        with self.assertRaises(ZoomError):
            self.world.zoombar("not-an-enrolled-credential")

    def test_user_credential_cannot_open_the_bootstrap_builder(self):
        with self.assertRaises(ZoomError):
            self.world.admin(self.alice_key)

    def test_public_zoombar_constructor_does_not_accept_a_known_actor_id_as_a_key(self):
        identity = self.alice.identity()
        with self.assertRaises(ZoomError):
            Zoombar(self.world, identity["id"], self.alice.session_id)

    def test_read_only_default_root_access_does_not_allow_writing(self):
        read_only = self.world.zoombar(self.builder.actor("READ_ONLY"))
        with self.assertRaises(ZoomError):
            read_only.put({"changed": True})

    def test_revoked_read_access_takes_effect_on_an_existing_session(self):
        self.enter_a()
        reference = self.alice.put([1, 2, 3])
        self.builder.revoke(self.alice_key, "A", rights=("read",))
        with self.assertRaises(ZoomError):
            self.alice.read(reference)

    def test_revoked_move_access_requires_safe_return(self):
        self.enter_a()
        self.builder.revoke(self.alice_key, "A", rights=("move",))
        self.assertEqual(self.alice.zoom_out(), "SAFE_RETURN")
        self.assertEqual(self.alice.path(), ["MASTER", "BRIDGE_1"])

    def test_an_actor_can_have_an_explicit_independent_root(self):
        key = self.builder.actor("B_ROOT", root="B")
        bar = self.world.zoombar(key)
        self.assertEqual(bar.path(), ["B"])
        with self.assertRaises(ZoomError):
            self.builder.revoke(key, "B", rights=("move",))

    def test_url_walk_checks_each_step(self):
        self.alice.walk("zoom://world/MASTER/BRIDGE_1/A/LAYER_1/B")
        self.assertEqual(self.alice.path(), ["MASTER", "BRIDGE_1", "A", "LAYER_1", "B"])

    def test_a_url_cannot_teleport_to_a_distant_world(self):
        with self.assertRaises(ZoomError):
            self.alice.walk("zoom://world/MASTER/B")
        self.assertEqual(self.alice.path(), ["MASTER"])

    def test_url_rejects_external_schemes_and_authorities(self):
        for address in ("https://example.invalid/MASTER", "zoom://other/MASTER"):
            with self.subTest(address=address):
                with self.assertRaises(ZoomError):
                    self.alice.walk(address)

    def test_unicode_url_names_are_decoded_without_becoming_a_jump(self):
        self.builder.lens("배달", label="배달 세계")
        self.builder.connect("MASTER", "배달")
        self.builder.grant(self.alice_key, "배달")
        self.alice.walk("zoom://world/MASTER/" + quote("배달", safe=""))
        self.assertEqual(self.alice.path(), ["MASTER", "배달"])

    def test_a_bookmark_is_a_target_reference_and_uses_real_connections(self):
        self.builder.bookmark(self.alice_key, "Go to B", "B")
        self.alice.bookmark("Go to B")
        self.assertEqual(self.alice.path(), ["MASTER", "BRIDGE_1", "A", "LAYER_1", "B"])

    def test_knowing_a_bookmark_does_not_supply_missing_access(self):
        self.builder.bookmark(self.alice_key, "Private", "PRIVATE")
        with self.assertRaises(ZoomError):
            self.alice.bookmark("Private")
        self.assertEqual(self.alice.here(), "MASTER")

    def test_unknown_bookmark_cannot_change_position(self):
        before = self.alice.path()
        with self.assertRaises(ZoomError):
            self.alice.bookmark("does-not-exist")
        self.assertEqual(self.alice.path(), before)

    def test_hash_storage_is_a_snapshot_of_the_supplied_value(self):
        self.enter_a()
        original = {"days": [[1, 2], [3]], "memo": "비 옴"}
        reference = self.alice.put(original)
        original["days"][0].append(99)
        read_back = self.alice.read(reference)
        self.assertEqual(read_back, {"days": [[1, 2], [3]], "memo": "비 옴"})
        read_back["days"].clear()
        self.assertEqual(self.alice.read(reference)["days"], [[1, 2], [3]])

    def test_hash_knowledge_does_not_cross_the_current_world_boundary(self):
        self.enter_a()
        reference = self.alice.put({"secret": "A-only"})
        self.alice.zoom_in("LAYER_1")
        with self.assertRaises(ZoomError):
            self.alice.read(reference)
        self.alice.zoom_out()
        self.assertEqual(self.alice.read(reference), {"secret": "A-only"})

    def test_move_permission_does_not_imply_data_read_permission(self):
        self.enter_a()
        reference = self.alice.put({"value": 17})
        restricted = self.builder.actor("READ_RESTRICTED")
        for uid in ("MASTER", "BRIDGE_1", "A"):
            self.builder.grant(restricted, uid, rights=("move",))
        visitor = self.world.zoombar(restricted)
        self.enter_a(visitor)
        with self.assertRaises(ZoomError):
            visitor.read(reference)

    def test_real_changes_form_a_verifiable_history(self):
        self.enter_a()
        self.alice.put([1, 2, 3])
        self.alice.zoom_out()
        report = self.world.verify_history()
        self.assertTrue(report["valid"])
        self.assertGreater(report["events"], 0)

    def test_central_execution_records_a_result_hash_without_a_business_return(self):
        self.enter_a()
        self.builder.contract({
            "BASE_PIN": "MASTER", "COMMON_ACTION": "calculate", "INNER_LENS": "A",
            "UNIQUE_ACTION": "total", "algorithm": "total", "version": 1,
        })
        parameter = self.alice.put({
            "BASE_PIN": "MASTER", "COMMON_ACTION": "calculate", "INNER_LENS": "A",
            "UNIQUE_ACTION": "total", "data": [4500, 3800, 5200],
        })
        self.assertIsNone(self.alice.run(parameter))
        done = next(event for event in self.alice.events() if event["kind"] == "CYCLE_DONE")
        result = self.alice.read(done["body"]["result_hash"])
        self.assertEqual(result["result"], 13_500)
        self.assertEqual(result["parameter_hash"], parameter)
        self.assertEqual(self.alice.path(), ["MASTER", "BRIDGE_1", "A"])

    def install_total(self):
        self.builder.contract({
            "BASE_PIN": "MASTER", "COMMON_ACTION": "calculate", "INNER_LENS": "A",
            "UNIQUE_ACTION": "total", "algorithm": "total",
        })

    def total_request(self, data):
        return {
            "BASE_PIN": "MASTER", "COMMON_ACTION": "calculate", "INNER_LENS": "A",
            "UNIQUE_ACTION": "total", "data": data,
        }

    def test_bad_execution_input_never_produces_a_success_event(self):
        self.enter_a()
        self.install_total()
        parameter = self.alice.put(self.total_request([1, True]))
        with self.assertRaises(ExecutionError):
            self.alice.run(parameter)
        self.assertNotIn("CYCLE_DONE", [event["kind"] for event in self.alice.events()])
        self.assertTrue(self.world.verify_history()["valid"])

    def test_execute_permission_does_not_replace_write_permission(self):
        self.enter_a()
        self.install_total()
        parameter = self.alice.put(self.total_request([1, 2]))
        self.builder.revoke(self.alice_key, "A", rights=("write",))
        with self.assertRaises(ZoomError):
            self.alice.run(parameter)
        self.assertNotIn("CYCLE_DONE", [event["kind"] for event in self.alice.events()])

    def test_a_detached_zoombar_path_cannot_authorize_execution(self):
        self.enter_a()
        self.install_total()
        parameter = self.alice.put(self.total_request([1, 2]))
        self.builder.disconnect("root_bridge")
        with self.assertRaises(ZoomError):
            self.alice.run(parameter)
        self.assertNotIn("CYCLE_DONE", [event["kind"] for event in self.alice.events()])

    def test_inner_lens_in_a_parameter_cannot_change_the_execution_target(self):
        self.enter_a()
        self.install_total()
        request = self.total_request([1, 2])
        request["INNER_LENS"] = "B"
        parameter = self.alice.put(request)
        with self.assertRaises(ZoomError):
            self.alice.run(parameter)
        self.assertEqual(self.alice.here(), "A")

    def test_concurrent_independent_sessions_keep_paths_data_and_chain_consistent(self):
        keys = [self.builder.actor("WORKER_" + str(index)) for index in range(4)]
        for key in keys:
            for uid in ("MASTER", "BRIDGE_1", "A"):
                self.builder.grant(key, uid)

        def work(pair):
            index, key = pair
            bar = self.world.zoombar(key, session_id="worker-" + str(index))
            self.enter_a(bar)
            for number in range(20):
                value = {"worker": index, "number": number}
                reference = bar.put(value)
                self.assertEqual(bar.read(reference), value)
            return bar.path()

        with ThreadPoolExecutor(max_workers=4) as pool:
            paths = list(pool.map(work, enumerate(keys)))
        self.assertEqual(paths, [["MASTER", "BRIDGE_1", "A"]] * 4)
        self.assertEqual(self.alice.here(), "MASTER")
        self.assertTrue(self.world.verify_history()["valid"])


class PersistenceContracts(unittest.TestCase):
    def test_restart_preserves_actor_path_values_and_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "world.sqlite")
            world = World(database)
            master_key = world.setup()
            builder = world.admin(master_key)
            builder.lens("A")
            builder.connect("MASTER", "A")
            actor_key = builder.actor("CODE")
            builder.grant(actor_key, "MASTER")
            builder.grant(actor_key, "A")
            bar = world.zoombar(actor_key, session_id="persisted-view")
            bar.zoom_in("A")
            reference = bar.put({"한국어": [1, 2, 3]})
            event_count = world.verify_history()["events"]
            world.close()

            reopened = World(database)
            try:
                restored = reopened.zoombar(actor_key, session_id="persisted-view")
                self.assertEqual(restored.path(), ["MASTER", "A"])
                self.assertEqual(restored.read(reference), {"한국어": [1, 2, 3]})
                self.assertIsNotNone(reopened.admin(master_key))
                report = reopened.verify_history()
                self.assertTrue(report["valid"])
                self.assertGreaterEqual(report["events"], event_count)
            finally:
                reopened.close()

    def check_tamper(self, statements):
        """Corrupt a disposable database, bypassing its append-only SQL guards."""
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "world.sqlite")
            world = World(database)
            key = world.setup()
            world.admin(key).lens("A")
            self.assertTrue(world.verify_history()["valid"])
            world.close()
            with sqlite3.connect(database) as connection:
                connection.execute("DROP TRIGGER events_no_update")
                connection.execute("DROP TRIGGER events_no_delete")
                for statement, parameters in statements:
                    connection.execute(statement, parameters)
            reopened = World(database)
            try:
                self.assertFalse(reopened.verify_history()["valid"])
            finally:
                reopened.close()

    def test_changed_history_payload_is_detected(self):
        self.check_tamper([("UPDATE events SET body=? WHERE sequence=1", ('{"forged":true}',))])

    def test_malformed_history_payload_is_reported_as_invalid(self):
        self.check_tamper([("UPDATE events SET body=? WHERE sequence=1", ("not-json",))])

    def test_removed_history_tail_is_detected(self):
        self.check_tamper([("DELETE FROM events WHERE sequence=(SELECT MAX(sequence) FROM events)", ())])

    def test_removed_entire_history_is_detected(self):
        self.check_tamper([("DELETE FROM events", ())])

    def test_history_cannot_be_updated_or_deleted_through_ordinary_sql(self):
        with tempfile.TemporaryDirectory() as directory:
            database = str(Path(directory) / "world.sqlite")
            world = World(database)
            world.setup()
            world.close()
            with sqlite3.connect(database) as connection:
                for statement in ("UPDATE events SET kind='forged'", "DELETE FROM events"):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(statement)

    def test_setup_cannot_silently_replace_existing_identity(self):
        with World() as world:
            key = world.setup()
            with self.assertRaises(ZoomError):
                world.setup()
            self.assertIsNotNone(world.admin(key))
            self.assertTrue(world.verify_history()["valid"])


class CommonEngineSourceContracts(unittest.TestCase):
    def test_domain_core_has_no_conditional_dispatch_syntax(self):
        tree = ast.parse(inspect.getsource(core))
        prohibited = (ast.If, ast.IfExp, ast.Match, ast.While)
        found = [
            (node.lineno, type(node).__name__)
            for node in ast.walk(tree)
            if isinstance(node, prohibited)
        ]
        self.assertEqual(found, [], "domain core must not grow per-case branch machinery")

    def test_domain_core_does_not_name_demo_business_worlds(self):
        tree = ast.parse(inspect.getsource(core))
        forbidden = {"DELIVERY", "COUPANG", "BAEMIN", "GPS", "YOGIYO", "PRIVATE"}
        literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        self.assertEqual(literals & forbidden, set())


if __name__ == "__main__":
    unittest.main()
