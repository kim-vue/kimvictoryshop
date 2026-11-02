"""Independent counterexamples for private collections and positional validity."""

import unittest

from zoomconnect.positional import Address, PositionalError, PositionalWorld


def select_slot(bar, address):
    bar.open(address.slot, bar.view()["revision"])


class PositionalReviewTests(unittest.TestCase):
    def setUp(self):
        self.world = PositionalWorld()
        self.master_key = self.world.setup()
        self.builder = self.world.admin(self.master_key)
        self.key = self.builder.actor("USER")
        self.bar = self.world.zoombar(self.key)

    def tearDown(self):
        self.world.close()

    def test_own_zoombar_is_a_visitable_board_without_making_history_a_route(self):
        own_history = Address(*self.bar.identity()["zoombar_address"])
        entry = self.builder.add(0, "Visit my history board", own_history)
        select_slot(self.bar, entry)
        self.assertEqual(self.bar.here(), own_history)
        # Appending this very visit must not invalidate the board header that
        # was entered. Runtime cursor changes are not a new LENS identity.
        self.assertEqual(self.bar.current()["kind"], "ZOOMBAR")
        projection = self.bar.view()
        self.assertGreaterEqual(len(projection["slots"]), 3)
        for item in projection["slots"][1:]:
            self.assertFalse(item["traversable"])
        with self.assertRaises(PositionalError) as failure:
            self.bar.open(1, projection["revision"])
        self.assertEqual(failure.exception.code, "NOT_TRAVERSABLE")
        self.assertEqual(self.bar.out(), "ENTRY")
        self.assertEqual(self.bar.here(), Address(0))
        self.assertTrue(self.world.verify_history()["valid"])

    def test_bookmark_and_old_history_are_not_new_physical_connections(self):
        destination = self.builder.collection("Destination")
        dead_end = self.builder.collection("Dead end")
        entry_destination = self.builder.add(0, "Destination", destination)
        entry_dead_end = self.builder.add(0, "Dead end", dead_end)
        self.builder.grant(self.key, destination)
        self.builder.grant(self.key, dead_end)
        bookmark = self.builder.bookmark(self.key, "Remember destination", [destination])

        select_slot(self.bar, entry_destination)
        self.bar.root()
        select_slot(self.bar, entry_dead_end)
        saved = next(board for board in self.bar.bookmarks() if board["collection"] == bookmark.collection)
        with self.assertRaises(PositionalError) as failure:
            self.bar.bookmark(bookmark.collection, 1, saved["revision"])
        self.assertEqual(failure.exception.code, "NO_ROUTE")
        self.assertEqual(self.bar.here(), dead_end)
        # Ordinary history return is still available; the bookmark itself did
        # not grant a new forward edge out of an otherwise terminal world.
        self.assertEqual(self.bar.out(), "ENTRY")
        self.assertEqual(self.bar.here(), Address(0))

    def test_round_trip_reorder_keeps_address_and_advances_location_revision(self):
        board = self.builder.collection("Cards")
        targets = [self.builder.collection(title) for title in ("A", "B", "C")]
        cards = [self.builder.add(board.collection, title, target) for title, target in zip(("A", "B", "C"), targets)]
        entry = self.builder.add(0, "Cards", board)
        pinned = self.builder.add(0, "Pinned coordinate", cards[0])
        for address in (board, *targets, *cards):
            self.builder.grant(self.key, address)
        select_slot(self.bar, entry)
        first = self.bar.view()
        self.builder.reorder(board.collection, 1, 3, first["revision"])
        second = self.bar.view()
        self.assertEqual(second["slots"][1]["title"], "B")
        self.builder.reorder(board.collection, 3, 1, second["revision"])
        third = self.bar.view()
        self.assertEqual(third["slots"][1]["title"], "A")
        self.assertEqual(first["slots"][1]["address"], third["slots"][1]["address"])
        self.assertLess(first["slots"][1]["revision"], second["slots"][1]["revision"])
        self.assertLess(second["slots"][1]["revision"], third["slots"][1]["revision"])
        self.bar.root()
        reference = self.bar.view()["slots"][pinned.slot]
        self.assertEqual(reference["target"], cards[0].as_list())
        select_slot(self.bar, pinned)
        self.assertEqual(self.bar.here(), cards[0])
        self.assertEqual(self.bar.current()["title"], "A")


if __name__ == "__main__":
    unittest.main()
