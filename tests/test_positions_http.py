"""Actual HTTP checks for the position-identity collection interface."""

import http.client
import json
import threading
import unittest

from zoomconnect.positions_server import make_position_server


class PositionHttpTests(unittest.TestCase):
    def setUp(self):
        self.server = make_position_server(0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port
        self.cookie = ""

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(timeout=3)
        self.server.server_close()
        self.server.application.demo.world.close()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        selected = {
            "Cookie": self.cookie,
            "Origin": f"http://127.0.0.1:{self.port}",
            "Content-Type": "application/json",
        }
        selected.update(headers or {})
        try:
            connection.request(method, path, None if body is None else json.dumps(body), selected)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def login(self):
        status, headers, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"POSITION", body)
        self.cookie = headers["Set-Cookie"].split(";", 1)[0]

    def action(self, action, actor="USER", **payload):
        status, _, body = self.request("POST", "/api/action", {"actor": actor, "action": action, **payload})
        return status, json.loads(body)

    def state(self, actor="USER"):
        status, _, body = self.request("GET", f"/api/state?actor={actor}")
        self.assertEqual(status, 200)
        return json.loads(body)

    def test_state_contains_real_common_collections(self):
        self.login()
        state = self.state()
        self.assertEqual(state["here"], [0, 0])
        for board in [state["view"], state["zoombar"], *state["bookmarks"]]:
            self.assertIn("collection", board)
            self.assertIn("revision", board)
            self.assertEqual(board["slots"][0]["position"], 0)
            self.assertEqual(board["slots"][0]["address"], [board["collection"], 0])
        self.assertTrue(state["integrity"]["valid"])

    def test_reorder_changes_the_occupant_without_changing_the_address(self):
        self.login()
        state = self.state()
        status, state = self.action("open", position=1, expected_revision=state["view"]["revision"])
        self.assertEqual(status, 200)
        before = state["view"]
        self.assertEqual(before["slots"][1]["target"], [2, 0])
        status, state = self.action("reorder", collection=1, from_position=1, to_position=2, expected_revision=before["revision"])
        self.assertEqual(status, 200)
        after = state["view"]
        self.assertEqual(after["slots"][1]["address"], [1, 1])
        self.assertEqual(after["slots"][1]["target"], [3, 0])
        self.assertGreater(after["slots"][1]["revision"], before["slots"][1]["revision"])
        status, error = self.action("open", position=1, expected_revision=before["revision"])
        self.assertEqual(status, 400)
        self.assertEqual(error["error"]["code"], "STALE_VIEW")
        status, state = self.action("open", position=1, expected_revision=after["revision"])
        self.assertEqual(status, 200)
        self.assertEqual(state["here"], [3, 0])
        self.assertEqual(self.state("AI")["here"], [0, 0])

    def test_a_separate_reference_keeps_its_coordinate(self):
        self.login()
        status, state = self.action("open", position=1, expected_revision=self.state()["view"]["revision"])
        status, state = self.action("reorder", collection=1, from_position=1, to_position=2, expected_revision=state["view"]["revision"])
        self.assertEqual(status, 200)
        status, state = self.action("root")
        status, state = self.action("open", position=2, expected_revision=state["view"]["revision"])
        self.assertEqual(state["view"]["slots"][1]["target"], [1, 1])
        status, state = self.action("open", position=1, expected_revision=state["view"]["revision"])
        self.assertEqual(status, 200)
        self.assertEqual(state["here"], [1, 1])
        self.assertEqual(state["current"]["target"], [3, 0])

    def test_bookmark_uses_a_real_slot_route(self):
        self.login()
        board = self.state()["bookmarks"][0]
        status, state = self.action("bookmark", collection=board["collection"], position=1, expected_revision=board["revision"])
        self.assertEqual(status, 200)
        self.assertEqual(state["path"], [[0, 0], [1, 0], [2, 0]])
        self.assertGreater(len(state["zoombar"]["slots"]), 3)

    def test_execution_uses_positional_contract_and_result_hash(self):
        self.login()
        board = self.state()["bookmarks"][0]
        status, state = self.action("bookmark", collection=board["collection"], position=1, expected_revision=board["revision"])
        self.assertEqual(status, 200)
        status, state = self.action("run", contract=state["contracts"][0], data=[4500, 3800, 5200])
        self.assertEqual(status, 200)
        self.assertEqual(state["here"], [2, 0])
        self.assertEqual(state["last_result"]["result"], 13500)
        self.assertTrue(state["returned_none"])
        self.assertTrue(state["result_hash"].startswith("pos1:"))
        self.assertTrue(any(event["kind"] == "CYCLE_DONE" and event["body"].get("result_hash") == state["result_hash"] for event in state["history"]))

    def test_transport_rejects_foreign_origin_and_wrong_current_board(self):
        self.login()
        self.assertEqual(self.request("POST", "/api/action", {"action": "root"}, {"Origin": "https://other.example"})[0], 403)
        status, error = self.action("reorder", collection=1, from_position=1, to_position=2, expected_revision=1)
        self.assertEqual(status, 400)
        self.assertEqual(error["error"]["code"], "NOT_CURRENT_COLLECTION")

    def test_mixed_workspace_separation_reconnection_and_real_bookmark(self):
        self.login()
        state = self.state()
        status, state = self.action("open", position=state["workspace_entry"], expected_revision=state["view"]["revision"])
        self.assertEqual(status, 200)
        status, state = self.action("mix", entries=state["mix_targets"], expected_revision=state["view"]["revision"])
        self.assertEqual(status, 200)
        positions = state["changed_slots"]
        self.assertEqual(len(positions), 3)
        before = state["view"]
        slot = positions[0][1]
        status, state = self.action("separate", position=slot, expected_revision=before["revision"])
        self.assertEqual(status, 200)
        self.assertFalse(state["view"]["slots"][slot]["enabled"])
        self.assertEqual(state["view"]["slots"][slot]["target"], before["slots"][slot]["target"])
        self.assertEqual(state["view"]["slots"][slot + 1:], before["slots"][slot + 1:])
        status, state = self.action("reconnect", position=slot, expected_revision=state["view"]["revision"])
        self.assertEqual(status, 200)
        self.assertTrue(state["view"]["slots"][slot]["enabled"])
        self.assertEqual(state["changed_slot"], positions[0])
        status, state = self.action("open", position=positions[2][1], expected_revision=state["view"]["revision"])
        self.assertEqual(status, 200)
        self.assertEqual(state["view"]["kind"], "BOOKMARK")
        status, state = self.action("separate", position=1, expected_revision=state["view"]["revision"])
        status, state = self.action("reconnect", position=1, expected_revision=state["view"]["revision"])
        self.assertEqual(status, 200)
        self.assertFalse(state["view"]["slots"][1]["traversable"])
        board = state["bookmarks"][0]
        status, state = self.action("bookmark", collection=board["collection"], position=1, expected_revision=board["revision"])
        self.assertEqual(status, 200)
        self.assertEqual(state["path"][-3:], [[0, 0], [1, 0], [2, 0]])
        self.assertTrue(state["integrity"]["valid"])

    def test_private_workspaces_are_not_shared_by_an_actor_selector(self):
        self.login()
        state = self.state("USER")
        status, error = self.action("open", actor="AI", position=state["workspace_entry"], expected_revision=self.state("AI")["view"]["revision"])
        self.assertEqual(status, 400)
        self.assertEqual(error["error"]["code"], "PRIVATE_COLLECTION")
        self.assertEqual(self.state("AI")["here"], [0, 0])

    def test_http_mix_does_not_accept_connection_policy_injection(self):
        self.login()
        before = self.state()
        status, error = self.action("mix", entries=[{"title": "Injected", "target": [1, 0], "traversable": True}], expected_revision=before["view"]["revision"])
        self.assertEqual(status, 400)
        self.assertEqual(error["error"]["code"], "BAD_ENTRY")
        self.assertEqual(self.state()["view"], before["view"])


if __name__ == "__main__":
    unittest.main()
