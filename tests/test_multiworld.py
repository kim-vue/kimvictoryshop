"""SQLite correctness across independent runtime handles, not just one RLock."""

from pathlib import Path
import tempfile
import threading
import time
import unittest

from zoomconnect.core import World, ZoomError


class IndependentRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Path(self.temp.name) / "world.sqlite"
        self.left = World(self.database)
        self.key = self.left.setup()
        self.admin = self.left.admin(self.key)
        self.right = World(self.database)

    def tearDown(self):
        self.right.close()
        self.left.close()
        self.temp.cleanup()

    def test_two_runtimes_cannot_append_incompatible_steps_to_one_session(self):
        for lens in ("A", "B"):
            self.admin.lens(lens)
            self.admin.connect("MASTER", lens)
        left = self.left.zoombar(self.key)
        right = self.right.zoombar(self.key)

        # Each handle has its own Python lock. Validation plus insertion must
        # therefore be serialized by the shared database transaction itself.
        for round_number in range(40):
            left.zoom_root()
            start = threading.Barrier(3)
            results = []

            def move(bar, target):
                start.wait(timeout=5)
                try:
                    bar.zoom_in(target)
                    results.append((target, "success"))
                except ZoomError as error:
                    results.append((target, error.code))
                except Exception as error:
                    results.append((target, repr(error)))

            threads = [
                threading.Thread(target=move, args=(left, "A")),
                threading.Thread(target=move, args=(right, "B")),
            ]
            for thread in threads:
                thread.start()
            start.wait(timeout=5)
            for thread in threads:
                thread.join(timeout=5)
                self.assertFalse(thread.is_alive(), "Concurrent movement did not terminate")

            with self.subTest(round=round_number):
                self.assertEqual(sorted(status for _, status in results), ["NOT_IN_LIST", "success"])
                path = left.path()
                self.assertEqual(len(path), 2, results)
                self.assertEqual(path[0], "MASTER")
                self.assertIn(path[1], {"A", "B"})
                self.assertEqual(right.path(), path)

        self.assertTrue(self.left.verify_history()["valid"])

    def test_history_verification_uses_one_snapshot_during_other_runtime_writes(self):
        bar = self.left.zoombar(self.key)
        # A nontrivial chain makes the verification overlap concurrent commits.
        for index in range(400):
            bar.put({"warmup": index})

        start = threading.Event()
        done = threading.Event()
        errors = []

        def append_events():
            start.set()
            try:
                for index in range(400):
                    bar.put({"concurrent": index})
                    if index % 10 == 0:
                        time.sleep(0.001)
            except Exception as error:
                errors.append(repr(error))
            finally:
                done.set()

        thread = threading.Thread(target=append_events)
        thread.start()
        self.assertTrue(start.wait(timeout=5))
        checks = []
        try:
            while not done.is_set():
                checks.append(self.right.verify_history())
                time.sleep(0.001)
        finally:
            thread.join(timeout=10)

        self.assertFalse(thread.is_alive(), "Concurrent writer did not terminate")
        self.assertEqual(errors, [])
        self.assertGreater(len(checks), 0)
        self.assertTrue(all(check["valid"] for check in checks), checks)
        final = self.right.verify_history()
        self.assertTrue(final["valid"])
        self.assertGreaterEqual(final["events"], 801)


if __name__ == "__main__":
    unittest.main()
