"""Mixed collections share one connect / separate / reconnect mechanism."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import threading
import unittest

from zoomconnect.positional import Address, PositionalError, PositionalWorld


class MixedConnections(unittest.TestCase):
    def setUp(self):
        self.world = PositionalWorld()
        self.master = self.world.setup()
        self.admin = self.world.admin(self.master)
        self.workspace = self.admin.collection('Mixed workspace')
        self.bridge = self.admin.collection('Bridge', kind='BRIDGE')
        self.layer = self.admin.collection('Layer', kind='LAYER')
        self.destination = self.admin.collection('Destination')
        self.secret = self.admin.collection('Not granted')
        self.entry = self.admin.connect(0, self.workspace, 'Workspace')
        self.admin.connect(0, self.destination, 'Destination')
        self.key = self.admin.actor('USER')
        self.other_key = self.admin.actor('AI')
        for key in (self.key, self.other_key):
            for address in (Address(0), self.workspace, self.bridge, self.layer, self.destination):
                self.admin.grant(key, address)
        self.bookmark = self.admin.bookmark(self.key, 'Real bookmark', [self.destination])
        self.bar = self.world.zoombar(self.key)
        self.bar.open(self.entry.slot, self.bar.view()['revision'])

    def tearDown(self):
        self.world.close()

    def revision(self):
        return self.bar.view()['revision']

    def entries(self):
        return [
            {'title': 'Bridge reference', 'target': self.bridge},
            {'title': 'Layer reference', 'target': self.layer},
            {'title': 'Bookmark reference', 'target': self.bookmark},
        ]

    def test_genuine_bookmark_bridge_layer_coexist_and_open_the_same_way(self):
        slots = self.bar.mix(self.entries(), self.revision())
        self.assertEqual([a.slot for a in slots], [1, 2, 3])
        for slot, target, kind in zip(slots, (self.bridge, self.layer, self.bookmark), ('BRIDGE', 'LAYER', 'BOOKMARK')):
            self.bar.open(slot.slot, self.revision())
            self.assertEqual(self.bar.here(), target)
            self.assertEqual(self.bar.view()['kind'], kind)
            self.assertEqual(self.bar.out(), 'ENTRY')
        self.assertTrue(self.world.verify_history()['valid'])

    def test_nested_mixed_route_uses_actual_open_steps(self):
        first = self.bar.connect(self.layer, 'Layer', self.revision())
        self.bar.open(first.slot, self.revision())
        second = self.bar.connect(self.bridge, 'Bridge', self.revision())
        self.bar.open(second.slot, self.revision())
        third = self.bar.connect(self.bookmark, 'Bookmark', self.revision())
        self.bar.open(third.slot, self.revision())
        self.assertEqual(self.bar.path(), [Address(0), self.workspace, self.layer, self.bridge, self.bookmark])

    def test_separate_preserves_position_target_and_other_parallel_connection(self):
        slots = self.bar.mix([
            {'title': 'First', 'target': self.bridge},
            {'title': 'Second', 'target': self.bridge},
            {'title': 'Layer', 'target': self.layer},
        ], self.revision())
        before = self.bar.view()
        self.bar.separate(slots[0].slot, before['revision'])
        after = self.bar.view()
        self.assertFalse(after['slots'][1]['enabled'])
        self.assertEqual(after['slots'][1]['target'], self.bridge.as_list())
        self.assertEqual(after['slots'][1]['address'], slots[0].as_list())
        self.assertFalse(after['slots'][1]['empty'])
        self.assertEqual(after['slots'][2:], before['slots'][2:])
        with self.assertRaisesRegex(PositionalError, 'DISABLED'):
            self.bar.open(1, after['revision'])
        self.bar.open(2, after['revision'])
        self.assertEqual(self.bar.here(), self.bridge)

    def test_reconnect_reuses_the_same_position_and_invalidates_old_view(self):
        slot = self.bar.connect(self.layer, 'Layer', self.revision())
        self.bar.separate(slot.slot, self.revision())
        disabled = self.bar.view()
        result = self.bar.reconnect(slot.slot, disabled['revision'])
        fresh = self.bar.view()
        self.assertEqual(result, slot)
        self.assertTrue(fresh['slots'][slot.slot]['enabled'])
        self.assertGreater(fresh['slots'][slot.slot]['revision'], disabled['slots'][slot.slot]['revision'])
        with self.assertRaisesRegex(PositionalError, 'STALE_VIEW'):
            self.bar.open(slot.slot, disabled['revision'])
        self.bar.open(slot.slot, fresh['revision'])
        self.assertEqual(self.bar.here(), self.layer)

    def test_retarget_only_changes_one_coordinate(self):
        slots = self.bar.mix(self.entries(), self.revision())
        before = self.bar.view()
        self.bar.reconnect(slots[0].slot, before['revision'], target=self.destination, title='New destination')
        after = self.bar.view()
        self.assertEqual(after['slots'][1]['address'], before['slots'][1]['address'])
        self.assertEqual(after['slots'][1]['target'], self.destination.as_list())
        self.assertEqual(after['slots'][2:], before['slots'][2:])

    def test_detaching_a_used_entry_requires_safe_return_then_reconnect(self):
        slot = self.bar.connect(self.bridge, 'Bridge', self.revision())
        before = self.bar.view()
        self.bar.open(slot.slot, before['revision'])
        self.admin.separate(self.workspace.collection, slot.slot, before['revision'])
        with self.assertRaisesRegex(PositionalError, 'STALE_PATH'):
            self.bar.view()
        self.assertEqual(self.bar.out(), 'SAFE_RETURN')
        self.assertEqual(self.bar.here(), self.workspace)
        self.bar.reconnect(slot.slot, self.revision())
        self.bar.open(slot.slot, self.revision())
        self.assertEqual(self.bar.here(), self.bridge)

    def test_explicit_hole_reuse_never_shifts_other_positions(self):
        slots = self.bar.mix(self.entries(), self.revision())
        self.bar.remove(slots[0].slot, self.revision())
        before = self.bar.view()
        result = self.bar.connect(self.destination, 'Replacement', before['revision'], position=slots[0].slot)
        self.assertEqual(result, slots[0])
        self.assertEqual(self.bar.view()['slots'][2:], before['slots'][2:])
        with self.assertRaisesRegex(PositionalError, 'OCCUPIED_SLOT'):
            self.bar.connect(self.bridge, 'No overwrite', self.revision(), position=slots[1].slot)

    def test_reconnect_a_removed_hole_requires_an_explicit_target(self):
        slot = self.bar.connect(self.bridge, 'Bridge', self.revision())
        self.bar.remove(slot.slot, self.revision())
        with self.assertRaisesRegex(PositionalError, 'EMPTY_SLOT'):
            self.bar.reconnect(slot.slot, self.revision())
        self.assertEqual(self.bar.reconnect(slot.slot, self.revision(), target=self.layer), slot)

    def test_mixed_batch_is_atomic_when_a_target_is_not_authorized(self):
        before = self.bar.view()
        event_count = self.world.verify_history()['events']
        with self.assertRaisesRegex(PositionalError, 'RIGHTS_DENIED'):
            self.bar.mix([self.entries()[0], {'title': 'Forbidden', 'target': self.secret}], before['revision'])
        self.assertEqual(self.bar.view(), before)
        self.assertEqual(self.world.verify_history()['events'], event_count)

    def test_mix_limits_and_invalid_shapes_do_not_modify_the_board(self):
        for entries in ([], [self.entries()[0]] * 257, [{'title': 'Missing'}]):
            before = self.bar.view()
            with self.assertRaises(PositionalError):
                self.bar.mix(entries, before['revision'])
            self.assertEqual(self.bar.view(), before)

    def test_target_move_alone_is_not_target_read_permission(self):
        self.admin.grant(self.key, self.secret, rights=('move',))
        with self.assertRaisesRegex(PositionalError, 'RIGHTS_DENIED'):
            self.bar.connect(self.secret, 'Unreadable', self.revision())

    def test_private_target_is_not_exposed_by_known_coordinates(self):
        private = self.admin.collection('Private', owner_key=self.other_key)
        with self.assertRaisesRegex(PositionalError, 'PRIVATE_COLLECTION'):
            self.bar.connect(private, 'Not mine', self.revision())

    def test_read_only_source_cannot_edit_connections(self):
        key = self.admin.actor('Read only')
        self.admin.grant(key, self.workspace, rights=('move', 'read'))
        bar = self.world.zoombar(key)
        bar.open(self.entry.slot, bar.view()['revision'])
        with self.assertRaisesRegex(PositionalError, 'RIGHTS_DENIED'):
            bar.connect(self.bridge, 'Denied', bar.view()['revision'])

    def test_real_bookmark_supports_separate_reconnect_without_creating_a_route(self):
        slot = self.bar.connect(self.bookmark, 'Book', self.revision())
        self.bar.open(slot.slot, self.revision())
        self.bar.separate(1, self.revision())
        self.bar.reconnect(1, self.revision())
        self.assertFalse(self.bar.view()['slots'][1]['traversable'])
        with self.assertRaisesRegex(PositionalError, 'NOT_TRAVERSABLE'):
            self.bar.open(1, self.revision())
        exit_slot = self.bar.connect(Address(0), 'Explicit real exit', self.revision())
        self.assertTrue(self.bar.view()['slots'][exit_slot.slot]['traversable'])
        self.bar.bookmark(self.bookmark.collection, 1, self.revision())
        self.assertEqual(self.bar.path()[-2:], [Address(0), self.destination])

    def test_protected_zoombar_cannot_be_edited_by_connection_operations(self):
        address = Address(*self.bar.identity()['zoombar_address'])
        self.admin.grant(self.key, address, rights=('write',))
        slot = self.bar.connect(address, 'Own history', self.revision())
        self.bar.open(slot.slot, self.revision())
        with self.assertRaisesRegex(PositionalError, 'PROTECTED_COLLECTION'):
            self.bar.connect(self.bridge, 'No journal overwrite', self.revision())

    def test_same_target_can_be_used_in_independent_collections(self):
        slot = self.bar.connect(self.bridge, 'Here', self.revision())
        self.bar.open(slot.slot, self.revision())
        other = self.bar.connect(self.layer, 'Elsewhere', self.revision())
        other_before = self.bar.view()
        self.bar.out()
        self.bar.separate(slot.slot, self.revision())
        self.bar.reconnect(slot.slot, self.revision())
        self.bar.open(slot.slot, self.revision())
        self.assertEqual(self.bar.view()['slots'][other.slot], other_before['slots'][other.slot])


class MixedConcurrency(unittest.TestCase):
    def test_two_batches_using_one_view_cannot_both_apply(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'mixed.sqlite'
            first = PositionalWorld(path)
            key = first.setup()
            admin = first.admin(key)
            target = admin.collection('Target')
            a = first.zoombar(key, 'shared')
            second = PositionalWorld(path)
            try:
                b = second.zoombar(key, 'shared')
                revision = a.view()['revision']
                barrier = threading.Barrier(2)
                def perform(bar):
                    barrier.wait(timeout=5)
                    try:
                        return bar.mix([{'title': 'A', 'target': target}, {'title': 'B', 'target': target}], revision)
                    except PositionalError as error:
                        return error.code
                with ThreadPoolExecutor(max_workers=2) as pool:
                    results = list(pool.map(perform, (a, b)))
                self.assertEqual(sum(isinstance(r, list) for r in results), 1)
                self.assertIn('STALE_VIEW', results)
                self.assertEqual(len(a.view()['slots']), 3)
                self.assertTrue(first.verify_history()['valid'])
            finally:
                second.close()
                first.close()


if __name__ == '__main__':
    unittest.main()
