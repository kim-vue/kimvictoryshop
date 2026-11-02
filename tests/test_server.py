import http.client
import json
import threading
import unittest

from zoomconnect.server import make_server


class HttpGatewayTests(unittest.TestCase):
    def setUp(self):
        self.server = make_server(0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port
        self.cookie = ""

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(timeout=3)
        self.server.server_close()
        self.server.application.demo.world.close()

    def request(self, method, path, data=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        selected = {
            "Cookie": self.cookie,
            "Origin": f"http://127.0.0.1:{self.port}",
            "Content-Type": "application/json",
        }
        selected.update(headers or {})
        body = None if data is None else json.dumps(data)
        try:
            connection.request(method, path, body=body, headers=selected)
            response = connection.getresponse()
            content = response.read()
            return response.status, dict(response.getheaders()), content
        finally:
            connection.close()

    def login_demo(self):
        status, headers, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.cookie = headers["Set-Cookie"].split(";", 1)[0]
        return body

    def action(self, action, actor="USER", **payload):
        status, _, body = self.request("POST", "/api/action", {"actor": actor, "action": action, **payload})
        return status, json.loads(body)

    def test_demo_page_and_authenticated_state(self):
        body = self.login_demo()
        self.assertIn(b"ZOOMCONNECT", body)
        status, _, body = self.request("GET", "/api/state?actor=USER")
        state = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(state["path"], ["MASTER"])
        self.assertEqual(len(state["actors"]), 5)
        self.assertTrue(state["integrity"]["valid"])

    def test_no_session_no_api(self):
        self.assertEqual(self.request("GET", "/api/state")[0], 403)
        self.assertEqual(self.action("root")[0], 403)

    def test_cross_origin_and_rebinding_denied(self):
        self.login_demo()
        self.assertEqual(self.request("POST", "/api/action", {"action": "root"}, {"Origin": "https://other.example"})[0], 403)
        self.assertEqual(self.request("GET", "/", headers={"Host": "attacker.example"})[0], 403)

    def test_direct_jump_fails_and_bookmark_really_travels(self):
        self.login_demo()
        status, data = self.action("enter", target="COUPANG")
        self.assertEqual(status, 400)
        self.assertEqual(data["error"]["code"], "NOT_IN_LIST")
        status, state = self.action("bookmark", name="쿠팡 정산")
        self.assertEqual(status, 200)
        self.assertEqual(state["path"], ["MASTER", "DELIVERY", "COUPANG"])
        self.assertTrue(any(event["kind"] == "ZOOM_IN" for event in state["history"]))
        status, _, raw = self.request("GET", "/api/state?actor=AI")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)["path"], ["MASTER"])

    def test_hash_execution_returns_recorded_result(self):
        self.login_demo()
        status, state = self.action("bookmark", name="쿠팡 정산")
        self.assertEqual(status, 200)
        status, state = self.action("run", contract=state["contracts"][0], data=[4500, 3800, 5200])
        self.assertEqual(status, 200)
        self.assertTrue(state["returned_none"])
        self.assertEqual(state["last_result"]["result"], 13500)
        self.assertTrue(state["parameter_hash"].startswith("zc1:"))
        self.assertTrue(state["result_hash"].startswith("zc1:"))
        self.assertTrue(state["integrity"]["valid"])

    def test_bad_commands_and_file_paths_not_exposed(self):
        self.login_demo()
        self.assertEqual(self.action("admin")[0], 400)
        self.assertEqual(self.request("GET", "/../../schema.sql")[0], 404)
        self.assertEqual(self.action("root", actor="unregistered")[0], 400)
        self.assertEqual(self.request("POST", "/api/action", {"action": "root"}, {"Content-Type": "text/plain"})[0], 415)


if __name__ == "__main__":
    unittest.main()
