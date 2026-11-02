"""Position-identity prototype. Collections and cells have no hidden world IDs.

An address is precisely (collection-list position, cell-list position). Reorder
moves records, never addresses or references. Every collection uses one common
storage, projection and revision mechanism; ``kind`` is presentation metadata.
This is an authenticated local prototype, not a hostile-Python sandbox or a
complete MASTER approval system.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from functools import wraps
from hashlib import sha256
import hmac
import json
import secrets
import sqlite3
from threading import RLock
from urllib.parse import quote, unquote, urlsplit


class PositionalError(Exception):
    def __init__(self, code, message=''):
        self.code = code
        self.message = f'{code}: {message}'.rstrip(': ')
        super().__init__(self.message)


def _require(condition, code, message=''):
    """Ordinary validation, explicitly not a LENS-kind dispatcher."""
    if not condition:
        raise PositionalError(code, message)


@dataclass(frozen=True, order=True)
class Address:
    collection: int
    slot: int = 0

    def __post_init__(self):
        _require(type(self.collection) is int and type(self.slot) is int
                 and self.collection >= 0 and self.slot >= 0, 'BAD_ADDRESS')

    def as_list(self):
        return [self.collection, self.slot]

    def text(self):
        return f'{self.collection}:{self.slot}'


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False)


def _hash(value):
    return sha256(value.encode('utf-8')).hexdigest()


def _copy(value):
    return json.loads(_canonical(value))


def _addr(value):
    _require(isinstance(value, Address), 'BAD_ADDRESS')
    return value


def _from_list(value):
    _require(isinstance(value, list) and len(value) == 2, 'BAD_ADDRESS')
    return Address(*value)


def _text(value, limit=256):
    _require(isinstance(value, str) and 0 < len(value) <= limit
             and '\x00' not in value, 'BAD_TEXT')
    return value


def _key(value):
    _require(isinstance(value, str) and 20 <= len(value) <= 512, 'BAD_CREDENTIAL')
    return _hash(value)


def _board(state, collection):
    _require(type(collection) is int and 0 <= collection < len(state['boards']), 'UNKNOWN_COLLECTION')
    board = state['boards'][collection]
    _require(board is not None, 'EMPTY_COLLECTION')
    return board


def _cell(state, address, code='EMPTY_TARGET'):
    address = _addr(address)
    board = _board(state, address.collection)
    _require(address.slot < len(board['slots']), code)
    cell = board['slots'][address.slot]
    _require(cell['record'] is not None, code)
    return cell


def _actor(state, credential):
    digest = _key(credential)
    _require(digest in state['actors'], 'BAD_CREDENTIAL')
    return digest, state['actors'][digest]


def _private(board, actor):
    _require(board['owner'] is None or board['owner'] == actor, 'PRIVATE_COLLECTION')


def _allowed(state, actor, address, right):
    board = _board(state, address.collection)
    if board['owner'] is not None and board['owner'] != actor:
        return False
    principal = state['actors'][actor]
    return actor == state['master'] or right in principal['grants'].get(address.text(), [])


def _permission(state, actor, address, right):
    _require(_allowed(state, actor, address, right), 'RIGHTS_DENIED', right)


def _grant(state, actor, address, rights):
    _cell(state, address)
    selected = tuple(rights)
    _require(all(r in ('move', 'read', 'write', 'execute') for r in selected), 'BAD_RIGHT')
    entries = state['actors'][actor]['grants']
    entries[address.text()] = sorted(set(entries.get(address.text(), [])) | set(selected))


def _tick(state):
    """A validation clock, not identity: view revisions are unique across boards."""
    state['clock'] += 1
    return state['clock']


def _invalidate_referrers(state, changed_addresses):
    """Invalidate views of direct references, without rewriting any reference.

    Cell versions describe occupants. Board versions additionally describe the
    selection view, so a target changing elsewhere invalidates an old view even
    though this board's reference still contains the exact same coordinates.
    """
    changed = {tuple(_addr(address).as_list()) for address in changed_addresses}
    for board in state['boards']:
        for cell in board['slots']:
            record = cell['record']
            if record is not None and record['target'] is not None and tuple(record['target']) in changed:
                board['revision'] = _tick(state)
                break


def _new_board(state, title, kind, owner=None, protected=False, travel_enabled=True):
    collection = len(state['boards'])
    header = {'title': _text(title), 'kind': _text(kind, 64), 'target': None,
              'enabled': True, 'traversable': False, 'metadata': {}}
    state['boards'].append({'revision': _tick(state), 'owner': owner, 'protected': protected,
                            'travel_enabled': travel_enabled,
                            'runtime': {},
                            'slots': [{'revision': 1, 'record': header}]})
    return Address(collection, 0)


def _append(state, collection, title, target, enabled=True, metadata=None, traversable=None):
    board = _board(state, collection)
    _cell(state, target)
    _require(type(enabled) is bool, 'BAD_ENABLED')
    record = {'title': _text(title), 'kind': 'REFERENCE', 'target': target.as_list(),
              'enabled': enabled, 'traversable': board['travel_enabled'],
              'metadata': _copy(metadata or {})}
    if traversable is not None:
        record['traversable'] = bool(traversable)
    position = len(board['slots'])
    board['slots'].append({'revision': 1, 'record': record})
    board['revision'] = _tick(state)
    return Address(collection, position)


def _revision(board, expected):
    _require(type(expected) is int and expected == board['revision'], 'STALE_VIEW')


def _editable(state, collection, expected, *positions):
    board = _board(state, collection)
    _revision(board, expected)
    _require(not board['protected'], 'PROTECTED_COLLECTION')
    _require(all(type(p) is int and 0 < p < len(board['slots']) for p in positions), 'PROTECTED_OR_UNKNOWN_SLOT')
    return board


def _reorder(state, collection, source, destination, expected):
    board = _editable(state, collection, expected, source, destination)
    _require(board['slots'][source]['record'] is not None, 'EMPTY_SLOT')
    records = [cell['record'] for cell in board['slots']]
    moved = records.pop(source)
    records.insert(destination, moved)
    for position in range(min(source, destination), max(source, destination) + 1):
        board['slots'][position]['record'] = records[position]
        board['slots'][position]['revision'] += 1
    board['revision'] = _tick(state)
    _invalidate_referrers(state, [Address(collection, position)
                                 for position in range(min(source, destination), max(source, destination) + 1)])


def _remove(state, collection, slot, expected):
    board = _editable(state, collection, expected, slot)
    cell = board['slots'][slot]
    _require(cell['record'] is not None, 'EMPTY_SLOT')
    cell['record'] = None
    cell['revision'] += 1
    board['revision'] = _tick(state)
    _invalidate_referrers(state, [Address(collection, slot)])


def _switch(state, collection, slot, enabled, expected):
    board = _editable(state, collection, expected, slot)
    cell = board['slots'][slot]
    _require(cell['record'] is not None, 'EMPTY_SLOT')
    _require(type(enabled) is bool, 'BAD_ENABLED')
    cell['record']['enabled'] = enabled
    cell['revision'] += 1
    board['revision'] = _tick(state)
    _invalidate_referrers(state, [Address(collection, slot)])


def _target(state, address):
    address = _addr(address)
    cell = _cell(state, address, 'EMPTY_TARGET')
    _require(cell['record']['enabled'], 'DISABLED_TARGET')
    return cell


def _connect(state, collection, target, title, expected, position=None):
    """One real connection cell, shared by every collection and caller."""
    board = _board(state, collection)
    _revision(board, expected)
    _require(not board['protected'], 'PROTECTED_COLLECTION')
    _target(state, target)
    _text(title)
    selected = len(board['slots']) if position is None else position
    _require(type(selected) is int and 0 < selected <= len(board['slots']), 'PROTECTED_OR_UNKNOWN_SLOT')
    if selected < len(board['slots']):
        _require(board['slots'][selected]['record'] is None, 'OCCUPIED_SLOT')
    board['travel_enabled'] = True
    if selected == len(board['slots']):
        address = _append(state, collection, title, target, traversable=True)
    else:
        cell = board['slots'][selected]
        cell['record'] = {'title': title, 'kind': 'REFERENCE', 'target': target.as_list(),
                          'enabled': True, 'traversable': True, 'metadata': {}}
        cell['revision'] += 1
        board['revision'] = _tick(state)
        address = Address(collection, selected)
    _invalidate_referrers(state, [address])
    return address


def _entries(entries):
    _require(isinstance(entries, list) and 1 <= len(entries) <= 256, 'BAD_ENTRIES')
    for entry in entries:
        _require(isinstance(entry, dict) and set(entry) == {'target', 'title'}, 'BAD_ENTRY')
        _addr(entry['target'])
        _text(entry['title'])
    return entries


def _mix(state, collection, entries, expected):
    entries = _entries(entries)
    board = _board(state, collection)
    _revision(board, expected)
    _require(not board['protected'], 'PROTECTED_COLLECTION')
    addresses = []
    for entry in entries:
        addresses.append(_connect(state, collection, entry['target'], entry['title'], board['revision']))
    return addresses


def _reconnect(state, collection, slot, expected, target=None, title=None):
    board = _editable(state, collection, expected, slot)
    cell = board['slots'][slot]
    record = cell['record']
    if record is None:
        _require(target is not None, 'EMPTY_SLOT')
        occupant = _target(state, target)
        selected_title = occupant['record']['title'] if title is None else title
        return _connect(state, collection, target, selected_title, expected, position=slot)
    destination = _from_list(record['target']) if target is None else _addr(target)
    _target(state, destination)
    selected_title = record['title'] if title is None else _text(title)
    record['target'] = destination.as_list()
    record['title'] = selected_title
    record['enabled'] = True
    # Existing traversal policy is deliberately retained, including False.
    cell['revision'] += 1
    board['revision'] = _tick(state)
    _invalidate_referrers(state, [Address(collection, slot)])
    return Address(collection, slot)


def _projection(state, collection):
    board = _board(state, collection)
    header = board['slots'][0]['record']
    entries = []
    for position, cell in enumerate(board['slots']):
        record = cell['record']
        item = {'position': position, 'address': [collection, position], 'revision': cell['revision'],
                'empty': record is None, 'protected': position == 0,
                'title': None, 'kind': None, 'target': None, 'enabled': False,
                'traversable': False, 'metadata': {}}
        if record is not None:
            item.update(_copy(record))
        entries.append(item)
    return {'collection': collection, 'address': [collection, 0], 'revision': board['revision'],
            'title': header['title'], 'kind': header['kind'], 'slots': entries,
            'metadata': {**_copy(header['metadata']), **_copy(board['runtime'])}}


def _store_value(state, address, value):
    revision = _cell(state, address)['revision']
    body = _canonical(value)
    _require(len(body.encode('utf-8')) <= 1048576, 'DATA_TOO_LARGE')
    digest = 'pos1:' + _hash(address.text() + ':' + str(revision) + ':' + body)
    state['objects'][digest] = {'address': address.as_list(), 'revision': revision, 'value': _copy(value)}
    return digest


def _load_value(state, address, hash):
    _text(hash, 128)
    _require(hash in state['objects'], 'UNKNOWN_HASH')
    item = state['objects'][hash]
    _require(item['address'] == address.as_list() and item['revision'] == _cell(state, address)['revision'], 'FOREIGN_OR_STALE_HASH')
    return _copy(item['value'])


def _transaction(event=None):
    def decorate(method):
        @wraps(method)
        def wrapped(self, *args, **kwargs):
            world = self._world
            connection = world._connection
            with world._lock, connection:
                connection.execute('BEGIN IMMEDIATE')
                state = json.loads(connection.execute('SELECT body FROM positional_state WHERE singleton=1').fetchone()[0])
                principal = self._authorize(state)
                self._event_context = {}
                result = method(self, state, *args, **kwargs)
                if event is not None:
                    body = _canonical(state)
                    anchor = connection.execute('SELECT head_hash,event_count FROM positional_state WHERE singleton=1').fetchone()
                    timestamp = datetime.now(timezone.utc).isoformat()
                    payload = {'state_digest': _hash(body), **self._event_context}
                    session = getattr(self, '_session_id', None)
                    signed = {'actor': principal, 'session': session, 'kind': event,
                              'body': payload, 'timestamp': timestamp, 'previous_hash': anchor[0]}
                    digest = _hash(_canonical(signed))
                    connection.execute('INSERT INTO positional_events(actor,session,kind,body,timestamp,previous_hash,hash) VALUES(?,?,?,?,?,?,?)',
                                       (principal, session, event, _canonical(payload), timestamp, anchor[0], digest))
                    connection.execute('UPDATE positional_state SET body=?,head_hash=?,event_count=? WHERE singleton=1',
                                       (body, digest, anchor[1] + 1))
                return result
        return wrapped
    return decorate


class PositionalWorld:
    def __init__(self, database=':memory:'):
        self._world = self
        self._lock = RLock()
        self._connection = sqlite3.connect(str(database), timeout=15, check_same_thread=False)
        connection = self._connection
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('PRAGMA busy_timeout=15000')
        connection.executescript('''
          CREATE TABLE IF NOT EXISTS positional_state(singleton INTEGER PRIMARY KEY CHECK(singleton=1),body TEXT NOT NULL,head_hash TEXT NOT NULL DEFAULT '',event_count INTEGER NOT NULL DEFAULT 0);
          CREATE TABLE IF NOT EXISTS positional_events(sequence INTEGER PRIMARY KEY AUTOINCREMENT,actor TEXT NOT NULL,session TEXT,kind TEXT NOT NULL,body TEXT NOT NULL,timestamp TEXT NOT NULL,previous_hash TEXT NOT NULL,hash TEXT NOT NULL UNIQUE);
          CREATE TRIGGER IF NOT EXISTS positional_events_no_update BEFORE UPDATE ON positional_events BEGIN SELECT RAISE(ABORT,'HISTORY_APPEND_ONLY'); END;
          CREATE TRIGGER IF NOT EXISTS positional_events_no_delete BEFORE DELETE ON positional_events BEGIN SELECT RAISE(ABORT,'HISTORY_APPEND_ONLY'); END;
        ''')
        initial = {'boards': [], 'actors': {}, 'sessions': {}, 'master': None, 'objects': {}, 'contracts': [], 'clock': 0}
        connection.execute('INSERT OR IGNORE INTO positional_state(singleton,body) VALUES(1,?)', (_canonical(initial),))
        connection.commit()

    def _authorize(self, state):
        return 'SYSTEM'

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        with self._lock:
            connection = self._connection
            connection.close()

    @_transaction('WORLD_CREATED')
    def setup(self, state):
        _require(state['master'] is None, 'ALREADY_SETUP')
        key = secrets.token_urlsafe(32)
        digest = _key(key)
        root = _new_board(state, 'MASTER', 'MASTER')
        state['master'] = digest
        state['actors'][digest] = {'name': 'MASTER', 'root': root.as_list(), 'grants': {}, 'bookmarks': []}
        _grant(state, digest, root, ('move', 'read', 'write', 'execute'))
        return key

    @_transaction()
    def admin(self, state, master_key):
        digest, actor = _actor(state, master_key)
        _require(hmac.compare_digest(digest, state['master']), 'MASTER_REQUIRED')
        return PositionalBuilder(self, digest)

    @_transaction('SESSION_OPENED')
    def zoombar(self, state, actor_key, session_id=None):
        digest, actor = _actor(state, actor_key)
        selected = 'default' if session_id is None else _text(session_id, 128)
        session = digest + ':' + selected
        if session not in state['sessions']:
            address = _new_board(state, f"{actor['name']} 이동 기록", 'ZOOMBAR', owner=digest, protected=True, travel_enabled=False)
            board = _board(state, address.collection)
            root = _from_list(actor['root'])
            cell = _cell(state, root)
            _append(state, address.collection, 'ROOT', root,
                    metadata={'target_revision': cell['revision'], 'previous_frame': None, 'via_address': None, 'via_revision': None}, traversable=False)
            board['runtime'] = {'cursor': 1, 'root_frame': 1}
            state['sessions'][session] = {'board': address.collection, 'actor': digest, 'session_id': selected}
            _grant(state, digest, address, ('move', 'read'))
        return PositionalZoombar(self, actor_key, selected)

    @_transaction()
    def verify_history(self, state):
        connection = self._connection
        events = connection.execute('SELECT sequence,actor,session,kind,body,timestamp,previous_hash,hash FROM positional_events ORDER BY sequence').fetchall()
        previous = ''
        valid = True
        last_state = None
        for expected, row in enumerate(events, 1):
            try:
                payload = json.loads(row[4])
                signed = {'actor': row[1], 'session': row[2], 'kind': row[3], 'body': payload,
                          'timestamp': row[5], 'previous_hash': row[6]}
                valid = valid and row[0] == expected and row[6] == previous and row[7] == _hash(_canonical(signed))
                last_state = payload['state_digest']
            except (ValueError, TypeError, KeyError):
                valid = False
            previous = row[7]
        anchor = connection.execute('SELECT head_hash,event_count FROM positional_state WHERE singleton=1').fetchone()
        valid = valid and previous == anchor[0] and len(events) == anchor[1]
        if events:
            valid = valid and last_state == _hash(_canonical(state))
        return {'valid': bool(valid), 'events': len(events)}


class PositionalBuilder:
    """Credentialed local configuration; not full MASTER approval machinery."""
    def __init__(self, world, credential_digest):
        self._world, self._credential_digest = world, credential_digest

    def _authorize(self, state):
        _require(hmac.compare_digest(self._credential_digest, state['master']), 'MASTER_REQUIRED')
        return _hash('actor:' + self._credential_digest)

    @_transaction('COLLECTION_CREATED')
    def collection(self, state, title, kind='COLLECTION', owner_key=None):
        owner = None
        if owner_key is not None:
            owner, actor = _actor(state, owner_key)
        address = _new_board(state, title, kind, owner=owner)
        if owner is not None:
            _grant(state, owner, address, ('move', 'read', 'write', 'execute'))
        return address

    @_transaction('REFERENCE_ADDED')
    def add(self, state, collection, title, target, enabled=True):
        board = _board(state, collection)
        _require(not board['protected'], 'PROTECTED_COLLECTION')
        return _append(state, collection, title, _addr(target), enabled)

    @_transaction('CONNECTED')
    def connect(self, state, collection, target, title, expected_revision=None, position=None):
        board = _board(state, collection)
        expected = board['revision'] if expected_revision is None else expected_revision
        address = _connect(state, collection, _addr(target), title, expected, position)
        self._event_context = {'source': [collection, 0], 'slot': address.as_list(),
                               'target': target.as_list(), 'enabled': True}
        return address

    @_transaction('MIXED')
    def mix(self, state, collection, entries, expected_revision=None):
        board = _board(state, collection)
        expected = board['revision'] if expected_revision is None else expected_revision
        addresses = _mix(state, collection, entries, expected)
        self._event_context = {'source': [collection, 0], 'slots': [a.as_list() for a in addresses]}
        return addresses

    @_transaction('SEPARATED')
    def separate(self, state, collection, slot, expected_revision):
        _switch(state, collection, slot, False, expected_revision)
        record = _cell(state, Address(collection, slot))['record']
        self._event_context = {'source': [collection, 0], 'slot': [collection, slot],
                               'target': _copy(record['target']), 'enabled': False}

    @_transaction('RECONNECTED')
    def reconnect(self, state, collection, slot, expected_revision, target=None, title=None):
        address = _reconnect(state, collection, slot, expected_revision, target, title)
        record = _cell(state, address)['record']
        self._event_context = {'source': [collection, 0], 'slot': address.as_list(),
                               'target': _copy(record['target']), 'enabled': True}
        return address

    @_transaction('REORDERED')
    def reorder(self, state, collection, from_slot, to_slot, expected_revision):
        _reorder(state, collection, from_slot, to_slot, expected_revision)

    @_transaction('REMOVED')
    def remove(self, state, collection, slot, expected_revision):
        _remove(state, collection, slot, expected_revision)

    @_transaction('SWITCHED')
    def switch(self, state, collection, slot, enabled, expected_revision):
        _switch(state, collection, slot, enabled, expected_revision)

    @_transaction('COLLECTIONS_SWAPPED')
    def swap_collections(self, state, left, right, left_revision, right_revision):
        """Move content between list positions without following or rewriting refs.

        Existing destination cell revisions remain attached to their positions.
        Shorter incoming content leaves tombstones, never compresses addresses.
        Root, private and runtime-protected collections cannot be swapped.
        """
        _require(type(left) is int and type(right) is int and left != right, 'BAD_SWAP')
        _require(left != 0 and right != 0, 'ROOT_COLLECTION')
        _require(all(actor['root'][0] not in (left, right) for actor in state['actors'].values()), 'ROOT_COLLECTION')
        boards = [_board(state, left), _board(state, right)]
        _revision(boards[0], left_revision)
        _revision(boards[1], right_revision)
        _require(all(board['owner'] is None and not board['protected'] for board in boards), 'PROTECTED_COLLECTION')
        original = _copy(boards)
        size = max(len(original[0]['slots']), len(original[1]['slots']))
        for destination, old, incoming in ((left, original[0], original[1]), (right, original[1], original[0])):
            slots = []
            for position in range(size):
                record = None
                if position < len(incoming['slots']):
                    record = incoming['slots'][position]['record']
                revision = _tick(state)
                if position < len(old['slots']):
                    revision = old['slots'][position]['revision'] + 1
                slots.append({'revision': revision, 'record': record})
            replacement = _copy(incoming)
            replacement['slots'] = slots
            replacement['revision'] = _tick(state)
            state['boards'][destination] = replacement
        _invalidate_referrers(state, [Address(collection, position)
                                     for collection in (left, right) for position in range(size)])

    @_transaction('ACTOR_CREATED')
    def actor(self, state, name, root=Address(0, 0)):
        root = _addr(root)
        _cell(state, root)
        _require(_board(state, root.collection)['owner'] is None, 'PRIVATE_COLLECTION')
        key = secrets.token_urlsafe(32)
        digest = _key(key)
        state['actors'][digest] = {'name': _text(name, 128), 'root': root.as_list(), 'grants': {}, 'bookmarks': []}
        _grant(state, digest, root, ('move', 'read'))
        _grant(state, digest, Address(root.collection, 0), ('read',))
        return key

    @_transaction('GRANTED')
    def grant(self, state, key, address, rights=('move', 'read', 'write', 'execute')):
        digest, actor = _actor(state, key)
        address = _addr(address)
        _private(_board(state, address.collection), digest)
        _grant(state, digest, address, rights)

    @_transaction('BOOKMARK_CREATED')
    def bookmark(self, state, key, title, targets):
        digest, actor = _actor(state, key)
        _require(isinstance(targets, list), 'BAD_TARGETS')
        address = _new_board(state, title, 'BOOKMARK', owner=digest, travel_enabled=False)
        for target in targets:
            cell = _cell(state, _addr(target))
            _append(state, address.collection, cell['record']['title'], target, traversable=False)
        actor['bookmarks'].append(address.collection)
        _grant(state, digest, address, ('move', 'read', 'write'))
        return address

    @_transaction('CONTRACT_INSTALLED')
    def contract(self, state, descriptor):
        from .execution import validate_binding
        binding = validate_binding(descriptor)
        for key in ('BASE_PIN', 'INNER_LENS'):
            parts = binding[key].split(':')
            _require(len(parts) == 2, 'BAD_ADDRESS')
            _cell(state, Address(*map(int, parts)))
        key = tuple(binding[k] for k in ('BASE_PIN', 'COMMON_ACTION', 'INNER_LENS', 'UNIQUE_ACTION', 'version'))
        _require(all(tuple(item['binding'][k] for k in ('BASE_PIN', 'COMMON_ACTION', 'INNER_LENS', 'UNIQUE_ACTION', 'version')) != key
                     for item in state['contracts']), 'CONTRACT_EXISTS')
        target = Address(*map(int, binding['INNER_LENS'].split(':')))
        state['contracts'].append({'binding': binding, 'target_revision': _cell(state, target)['revision']})


class PositionalZoombar:
    def __init__(self, world, credential, session_id):
        self._world = world
        self._credential_digest = _key(credential)
        self._session_id = session_id
        self._session_key = self._credential_digest + ':' + session_id

    def _authorize(self, state):
        _require(self._credential_digest in state['actors'], 'BAD_CREDENTIAL')
        _require(self._session_key in state['sessions'], 'UNKNOWN_SESSION')
        session = state['sessions'][self._session_key]
        _require(session['actor'] == self._credential_digest, 'SESSION_FORBIDDEN')
        return _hash('actor:' + self._credential_digest)

    def _board(self, state):
        return _board(state, state['sessions'][self._session_key]['board'])

    def _frames(self, state):
        board = self._board(state)
        cursor = board['runtime']['cursor']
        positions = []
        for _ in range(len(board['slots'])):
            if cursor is None:
                break
            _require(type(cursor) is int and 0 < cursor < len(board['slots']) and cursor not in positions, 'CORRUPT_PATH')
            positions.append(cursor)
            record = board['slots'][cursor]['record']
            _require(record is not None, 'CORRUPT_PATH')
            cursor = record['metadata']['previous_frame']
        _require(cursor is None, 'CORRUPT_PATH')
        return [(position, board['slots'][position]['record']) for position in reversed(positions)]

    def _here(self, state):
        return _from_list(self._frames(state)[-1][1]['target'])

    def _valid_prefix(self, state):
        count = 0
        previous = None
        for position, frame in self._frames(state):
            try:
                target = _from_list(frame['target'])
                cell = _cell(state, target)
                _require(cell['revision'] == frame['metadata']['target_revision'] and cell['record']['enabled'], 'STALE_PATH')
                _permission(state, self._credential_digest, target, 'move')
                if previous is not None:
                    via = _from_list(frame['metadata']['via_address'])
                    _require(via.collection == previous.collection, 'STALE_PATH')
                    link = _cell(state, via)
                    _require(link['revision'] == frame['metadata']['via_revision']
                             and link['record']['enabled'] and link['record']['traversable']
                             and link['record']['target'] == target.as_list(), 'STALE_PATH')
                count += 1
                previous = target
            except PositionalError:
                break
        return count

    def _valid(self, state):
        _require(self._valid_prefix(state) == len(self._frames(state)), 'STALE_PATH')

    def _view(self, state, collection):
        board = _board(state, collection)
        _private(board, self._credential_digest)
        _permission(state, self._credential_digest, Address(collection, 0), 'read')
        return _projection(state, collection)

    @_transaction()
    def identity(self, state):
        board = state['sessions'][self._session_key]['board']
        return {'name': state['actors'][self._credential_digest]['name'], 'session_id': self._session_id,
                'zoombar_address': [board, 0]}

    @_transaction()
    def here(self, state):
        return self._here(state)

    @_transaction()
    def path(self, state):
        return [_from_list(frame['target']) for position, frame in self._frames(state)]

    @_transaction()
    def view(self, state):
        self._valid(state)
        return self._view(state, self._here(state).collection)

    @_transaction()
    def current(self, state):
        self._valid(state)
        address = self._here(state)
        _permission(state, self._credential_digest, address, 'read')
        projection = _projection(state, address.collection)
        return projection['slots'][address.slot]

    @_transaction()
    def zoombar_view(self, state):
        collection = state['sessions'][self._session_key]['board']
        return self._view(state, collection)

    def _open(self, state, slot, expected_revision):
        self._valid(state)
        here = self._here(state)
        board = _board(state, here.collection)
        _private(board, self._credential_digest)
        _permission(state, self._credential_digest, Address(here.collection, 0), 'read')
        _revision(board, expected_revision)
        _require(type(slot) is int and 0 < slot < len(board['slots']), 'UNKNOWN_SLOT')
        via = Address(here.collection, slot)
        cell = _cell(state, via, 'EMPTY_SLOT')
        record = cell['record']
        _require(board['travel_enabled'] and record['traversable'], 'NOT_TRAVERSABLE')
        _require(record['enabled'], 'DISABLED')
        target = _from_list(record['target'])
        occupant = _cell(state, target, 'EMPTY_TARGET')
        _require(occupant['record']['enabled'], 'DISABLED_TARGET')
        _private(_board(state, target.collection), self._credential_digest)
        _permission(state, self._credential_digest, target, 'move')
        history = self._board(state)
        frames = self._frames(state)
        history_collection = state['sessions'][self._session_key]['board']
        frame = _append(state, history_collection, occupant['record']['title'], target,
                        metadata={'target_revision': occupant['revision'], 'previous_frame': frames[-1][0],
                                  'via_address': via.as_list(), 'via_revision': cell['revision']}, traversable=False)
        history['runtime']['cursor'] = frame.slot
        self._event_context = {'from': here.as_list(), 'via': via.as_list(), 'to': target.as_list(),
                               'target_revision': occupant['revision'], 'via_revision': cell['revision'],
                               'path_frame': frame.as_list()}

    @_transaction('ZOOM_IN')
    def open(self, state, slot, expected_revision):
        self._open(state, slot, expected_revision)

    @_transaction('ZOOM_OUT')
    def out(self, state):
        frames = self._frames(state)
        valid = self._valid_prefix(state)
        _require(valid > 0, 'ROOT_INVALID')
        if len(frames) == 1:
            mode, selected = 'ROOT', 0
        elif valid < len(frames):
            mode, selected = 'SAFE_RETURN', valid - 1
        else:
            mode, selected = 'ENTRY', len(frames) - 2
        board = self._board(state)
        board['runtime']['cursor'] = frames[selected][0]
        board['revision'] = _tick(state)
        self._event_context = {'mode': mode, 'at': frames[selected][1]['target']}
        if mode == 'SAFE_RETURN':
            self._event_context['reason'] = 'STALE_POSITION_OR_CONNECTION'
        return mode

    @_transaction('ZOOM_ROOT')
    def root(self, state):
        frames = self._frames(state)
        _require(self._valid_prefix(state) > 0, 'ROOT_INVALID')
        board = self._board(state)
        board['runtime']['cursor'] = frames[0][0]
        board['revision'] = _tick(state)
        self._event_context = {'at': frames[0][1]['target']}

    @_transaction('REORDERED')
    def reorder(self, state, from_slot, to_slot, expected_revision):
        self._valid(state)
        address = self._here(state)
        _permission(state, self._credential_digest, Address(address.collection, 0), 'write')
        _reorder(state, address.collection, from_slot, to_slot, expected_revision)

    def _edit_collection(self, state, expected_revision):
        """One authenticated current-board edit boundary for every kind."""
        self._valid(state)
        collection = self._here(state).collection
        board = _board(state, collection)
        _private(board, self._credential_digest)
        _permission(state, self._credential_digest, Address(collection, 0), 'write')
        _revision(board, expected_revision)
        _require(not board['protected'], 'PROTECTED_COLLECTION')
        return collection

    def _connection_target(self, state, target):
        target = _addr(target)
        _target(state, target)
        _private(_board(state, target.collection), self._credential_digest)
        _permission(state, self._credential_digest, target, 'move')
        _permission(state, self._credential_digest, target, 'read')
        return target

    @_transaction('CONNECTED')
    def connect(self, state, target, title, expected_revision, position=None):
        collection = self._edit_collection(state, expected_revision)
        target = self._connection_target(state, target)
        address = _connect(state, collection, target, title, expected_revision, position)
        self._event_context = {'source': [collection, 0], 'slot': address.as_list(),
                               'target': target.as_list(), 'enabled': True}
        return address

    @_transaction('MIXED')
    def mix(self, state, entries, expected_revision):
        collection = self._edit_collection(state, expected_revision)
        entries = _entries(entries)
        for entry in entries:
            self._connection_target(state, entry['target'])
        addresses = _mix(state, collection, entries, expected_revision)
        self._event_context = {'source': [collection, 0], 'slots': [a.as_list() for a in addresses],
                               'targets': [entry['target'].as_list() for entry in entries]}
        return addresses

    @_transaction('SEPARATED')
    def separate(self, state, slot, expected_revision):
        collection = self._edit_collection(state, expected_revision)
        _switch(state, collection, slot, False, expected_revision)
        record = _cell(state, Address(collection, slot))['record']
        self._event_context = {'source': [collection, 0], 'slot': [collection, slot],
                               'target': _copy(record['target']), 'enabled': False}

    @_transaction('RECONNECTED')
    def reconnect(self, state, slot, expected_revision, target=None, title=None):
        collection = self._edit_collection(state, expected_revision)
        board = _editable(state, collection, expected_revision, slot)
        record = board['slots'][slot]['record']
        destination = target
        if destination is None:
            _require(record is not None, 'EMPTY_SLOT')
            destination = _from_list(record['target'])
        self._connection_target(state, destination)
        address = _reconnect(state, collection, slot, expected_revision, target, title)
        record = _cell(state, address)['record']
        self._event_context = {'source': [collection, 0], 'slot': address.as_list(),
                               'target': _copy(record['target']), 'enabled': True}
        return address

    @_transaction('REMOVED')
    def remove(self, state, slot, expected_revision):
        self._valid(state)
        address = self._here(state)
        _permission(state, self._credential_digest, Address(address.collection, 0), 'write')
        _remove(state, address.collection, slot, expected_revision)

    @_transaction('SWITCHED')
    def switch(self, state, slot, enabled, expected_revision):
        self._valid(state)
        address = self._here(state)
        _permission(state, self._credential_digest, Address(address.collection, 0), 'write')
        _switch(state, address.collection, slot, enabled, expected_revision)

    @_transaction()
    def bookmarks(self, state):
        actor = state['actors'][self._credential_digest]
        return [self._view(state, collection) for collection in actor['bookmarks']]

    @_transaction()
    def _plan_bookmark(self, state, collection, slot, expected_revision):
        self._valid(state)
        actor = state['actors'][self._credential_digest]
        _require(collection in actor['bookmarks'], 'UNKNOWN_BOOKMARK')
        board = _board(state, collection)
        _revision(board, expected_revision)
        cell = _cell(state, Address(collection, slot), 'EMPTY_SLOT')
        _require(cell['record']['enabled'], 'DISABLED')
        target = _from_list(cell['record']['target'])
        _cell(state, target, 'EMPTY_TARGET')
        _permission(state, self._credential_digest, target, 'move')
        start = self._here(state)
        queue = deque([(start, [])])
        seen = {start}
        visits = 0
        while queue and visits < 10000:
            at, route = queue.popleft()
            visits += 1
            if at == target:
                return route
            if len(route) >= 64:
                continue
            source = _board(state, at.collection)
            if not _allowed(state, self._credential_digest, Address(at.collection, 0), 'read'):
                continue
            for position, candidate in enumerate(source['slots'][1:], 1):
                record = candidate['record']
                if record is None or not source['travel_enabled'] or not record['enabled'] or not record['traversable']:
                    continue
                destination = _from_list(record['target'])
                try:
                    occupant = _cell(state, destination)
                    _require(occupant['record']['enabled'], 'DISABLED_TARGET')
                    _permission(state, self._credential_digest, destination, 'move')
                except PositionalError:
                    continue
                if destination not in seen:
                    seen.add(destination)
                    queue.append((destination, route + [(position, source['revision'])]))
        raise PositionalError('NO_ROUTE', 'No authorized route within 64 steps / 10000 visits')

    def bookmark(self, bookmark_collection, slot, expected_revision):
        route = self._plan_bookmark(bookmark_collection, slot, expected_revision)
        for position, revision in route:
            self.open(position, revision)

    def walk(self, url):
        _text(url, 8192)
        parsed = urlsplit(url)
        raw_path = parsed.path
        parts = list(map(unquote, raw_path.strip('/').split('/')))
        root = self.path()[0]
        _require(parsed.scheme == 'zoom' and parsed.netloc == 'world' and not parsed.query
                 and not parsed.fragment and parts[0] == root.text(), 'BAD_URL')
        _require(all(part.isascii() and part.isdigit() for part in parts[1:]), 'BAD_URL')
        self.root()
        for selected in parts[1:]:
            view = self.view()
            self.open(int(selected), view['revision'])

    @_transaction()
    def url(self, state):
        frames = self._frames(state)
        root = _from_list(frames[0][1]['target']).text()
        positions = [str(frame['metadata']['via_address'][1]) for position, frame in frames[1:]]
        return 'zoom://world/' + '/'.join([root, *positions])

    @_transaction()
    def history(self, state, limit=30):
        _require(type(limit) is int and 1 <= limit <= 500, 'BAD_LIMIT')
        world = self._world
        connection = world._connection
        actor = _hash('actor:' + self._credential_digest)
        rows = connection.execute('SELECT sequence,kind,body,timestamp FROM positional_events WHERE actor=? AND session=? ORDER BY sequence DESC LIMIT ?',
                                  (actor, self._session_id, limit)).fetchall()
        return [{'sequence': r[0], 'kind': r[1], 'body': json.loads(r[2]), 'timestamp': r[3]} for r in rows]

    @_transaction('DATA_PUT')
    def put(self, state, value):
        self._valid(state)
        address = self._here(state)
        _permission(state, self._credential_digest, address, 'write')
        digest = _store_value(state, address, value)
        self._event_context = {'address': address.as_list(), 'revision': _cell(state, address)['revision'], 'hash': digest}
        return digest

    @_transaction()
    def read(self, state, hash):
        self._valid(state)
        address = self._here(state)
        _permission(state, self._credential_digest, address, 'read')
        return _load_value(state, address, hash)

    @_transaction()
    def contracts(self, state):
        self._valid(state)
        address = self._here(state)
        _permission(state, self._credential_digest, address, 'read')
        revision = _cell(state, address)['revision']
        return [_copy(item['binding']) for item in state['contracts']
                if item['binding']['INNER_LENS'] == address.text() and item['target_revision'] == revision]

    @_transaction('CYCLE_DONE')
    def run(self, state, parameter_hash):
        from .execution import evaluate
        self._valid(state)
        address = self._here(state)
        for right in ('read', 'write', 'execute'):
            _permission(state, self._credential_digest, address, right)
        request = _load_value(state, address, parameter_hash)
        _require(isinstance(request, dict) and request.get('INNER_LENS') == address.text(), 'INNER_NOT_HERE')
        path = {_from_list(frame['target']).text() for position, frame in self._frames(state)}
        _require(request.get('BASE_PIN') in path, 'BASE_PIN_NOT_IN_PATH')
        keys = ('BASE_PIN', 'COMMON_ACTION', 'INNER_LENS', 'UNIQUE_ACTION')
        matches = [item for item in state['contracts']
                   if all(item['binding'][key] == request.get(key) for key in keys)]
        _require(bool(matches), 'NO_CONTRACT')
        selected = max(matches, key=lambda item: item['binding']['version'])
        revision = _cell(state, address)['revision']
        _require(selected['target_revision'] == revision, 'STALE_CONTRACT')
        binding = selected['binding']
        value = evaluate(request, binding)
        result = {'result': value, 'contract_version': binding['version'], 'parameter_hash': parameter_hash}
        digest = _store_value(state, address, result)
        board = self._board(state)
        board['runtime']['last_result_hash'] = digest
        board['revision'] = _tick(state)
        self._event_context = {'parameter_hash': parameter_hash, 'result_hash': digest,
                               'address': address.as_list(), 'revision': revision,
                               'contract_version': binding['version']}

    @_transaction()
    def last_result_hash(self, state):
        return self._board(state)['runtime'].get('last_result_hash')
