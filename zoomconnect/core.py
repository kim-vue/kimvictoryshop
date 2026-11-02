"""A flat, credentialed LENS graph. Kinds never participate in navigation.

Movement uses the same relational edge/grant/path queries for every LENS.
There are no Python conditional statements, ternaries, match statements or
kind dispatch tables here. Generic missing-row/error handling is explicit;
SQLite predicates enforce the shared invariants, rather than emulating kinds.

This is a local gateway, not a sandbox against malicious Python reflection.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps
from hashlib import sha256
import json
from pathlib import Path
import secrets
import sqlite3
from threading import RLock
from urllib.parse import quote, unquote, urlsplit
from uuid import uuid4


class ZoomError(Exception):
    def __init__(self, code, message=''):
        self.code = code
        self.message = f'{code}: {message}'.rstrip(': ')
        super().__init__(self.message)


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def _digest(text):
    return sha256(text.encode('utf-8')).hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat()


def _event_digest(event):
    try:
        canonical = _canonical({'actor':event['actor'],'session':event['session'],'kind':event['kind'],
                                'body':json.loads(event['body']),'timestamp':event['timestamp'],
                                'previous_hash':event['previous_hash']})
        return _digest(canonical)
    except (ValueError, TypeError, KeyError):
        return None


def _one(connection, sql, parameters=(), code='ACCESS_DENIED'):
    """Shared relational assertion. Missing rows are failures, never fake results."""
    try:
        return next(connection.execute(sql, parameters))
    except StopIteration:
        raise ZoomError(code) from None


def _atomic(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        world = self._world
        lock = world._lock
        connection = world._connection
        with lock, connection:
            # Reserve the SQLite write transaction BEFORE any authorization or
            # path read. Independent World instances must validate and mutate
            # against one serialized snapshot, not deferred-BEGIN snapshots.
            connection.execute('BEGIN IMMEDIATE')
            try:
                return method(self, *args, **kwargs)
            except sqlite3.IntegrityError as error:
                raise ZoomError('CONSTRAINT', str(error)) from error
    return wrapped


_VALID_PREFIX = """
 SELECT COALESCE(MIN(f.position), (SELECT COUNT(*) FROM frames WHERE session=:session)) AS length
 FROM frames f
 WHERE f.session=:session AND (
   NOT EXISTS(SELECT 1 FROM lenses l WHERE l.uid=f.lens AND l.active=1)
   OR NOT EXISTS(SELECT 1 FROM grants g WHERE g.actor=:actor AND g.lens=f.lens AND g.right='move')
   OR (f.position>0 AND NOT EXISTS(
     SELECT 1 FROM connections c JOIN frames p ON p.session=f.session AND p.position=f.position-1
     WHERE c.uid=f.entry AND c.active=1 AND c.source=p.lens AND c.target=f.lens
   ))
 )
"""


class World:
    """Owns persistence, never exposes LENS implementation objects."""
    def __init__(self, database=':memory:'):
        self._world = self
        self._lock = RLock()
        self._connection = sqlite3.connect(str(database), timeout=15, check_same_thread=False)
        connection = self._connection
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys=ON')
        connection.execute('PRAGMA journal_mode=WAL')
        connection.execute('PRAGMA busy_timeout=15000')
        connection.executescript(Path(__file__).with_name('schema.sql').read_text(encoding='utf-8'))
        connection.commit()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        lock = self._lock
        connection = self._connection
        with lock:
            connection.close()

    def _audit(self, actor, session, kind, body):
        connection = self._connection
        previous = _one(connection, "SELECT COALESCE((SELECT hash FROM events ORDER BY sequence DESC LIMIT 1),'') AS hash")['hash']
        timestamp = _now()
        canonical = _canonical({'actor': actor, 'session': session, 'kind': kind, 'body': body, 'timestamp': timestamp, 'previous_hash': previous})
        digest = _digest(canonical)
        connection.execute('INSERT INTO events(actor,session,kind,body,timestamp,previous_hash,hash) VALUES(?,?,?,?,?,?,?)',
                           (actor, session, kind, _canonical(body), timestamp, previous, digest))
        connection.execute('UPDATE settings SET head_hash=?,event_count=event_count+1 WHERE id=1',(digest,))

    def _actor(self, key):
        _one(self._connection, 'SELECT 1 WHERE typeof(?)=\'text\' AND length(?) BETWEEN 20 AND 512', (key,key), 'BAD_CREDENTIAL')
        return _one(self._connection, 'SELECT * FROM actors WHERE key_digest=? AND active=1', (_digest(key),), 'BAD_CREDENTIAL')

    @_atomic
    def setup(self, root='MASTER'):
        connection = self._connection
        _one(connection, 'SELECT 1 WHERE NOT EXISTS(SELECT 1 FROM settings)', code='ALREADY_SETUP')
        key, actor = secrets.token_urlsafe(32), uuid4().hex
        connection.execute('INSERT INTO lenses(uid,label,kind) VALUES(?,?,?)', (root,root,'MASTER'))
        connection.execute('INSERT INTO actors(id,name,key_digest,role,root) VALUES(?,?,?,?,?)', (actor,'MASTER',_digest(key),'MASTER',root))
        connection.execute('INSERT INTO settings(id,root,master_actor) VALUES(1,?,?)', (root,actor))
        connection.executemany('INSERT INTO grants(actor,lens,right) VALUES(?,?,?)', ((actor,root,right) for right in ('move','read','write','execute')))
        self._audit(actor,None,'WORLD_CREATED',{'root':root})
        return key

    @_atomic
    def admin(self, master_key):
        actor = self._actor(master_key)
        _one(self._connection, 'SELECT 1 FROM settings WHERE master_actor=?', (actor['id'],), 'MASTER_REQUIRED')
        return _Builder(self, actor['id'])

    @_atomic
    def zoombar(self, actor_key, session_id=None):
        connection = self._connection
        actor = self._actor(actor_key)
        root = actor['root']
        chosen = _one(connection, 'SELECT COALESCE(?,?) AS id', (session_id,actor['id']+':default'))['id']
        connection.execute('INSERT OR IGNORE INTO sessions(id,actor,root) VALUES(?,?,?)',(chosen,actor['id'],root))
        _one(connection,'SELECT 1 FROM sessions WHERE id=? AND actor=?',(chosen,actor['id']),'SESSION_FORBIDDEN')
        connection.execute('INSERT OR IGNORE INTO frames(session,position,lens,entry) VALUES(?,0,?,NULL)',(chosen,root))
        return Zoombar(self,actor_key,chosen)

    @_atomic
    def verify_history(self):
        connection = self._connection
        events = list(connection.execute('SELECT * FROM events ORDER BY sequence'))
        previous = ''
        matches = []
        for index,event in enumerate(events,1):
            matches.extend((event['sequence']==index,event['previous_hash']==previous,event['hash']==_event_digest(event)))
            previous = event['hash']
        anchor=_one(connection,"SELECT COALESCE((SELECT head_hash FROM settings),'') AS hash,COALESCE((SELECT event_count FROM settings),0) AS n")
        matches.extend((previous==anchor['hash'],len(events)==anchor['n']))
        return {'valid':all(matches), 'events':len(events)}

class _Builder:
    """Explicit MASTER configuration handle; not a production approval workflow."""
    def __init__(self, world, actor):
        self._world, self._actor_id = world, actor

    def _auth(self):
        world = self._world
        return _one(world._connection, 'SELECT 1 FROM actors a JOIN settings s ON s.master_actor=a.id WHERE a.id=? AND a.active=1', (self._actor_id,), 'MASTER_REQUIRED')

    @_atomic
    def lens(self, uid, label=None, kind='LENS'):
        self._auth()
        world = self._world
        connection = world._connection
        connection.execute('INSERT INTO lenses(uid,label,kind) VALUES(?,COALESCE(?,?),?)',(uid,label,uid,kind))
        connection.executemany('INSERT INTO grants(actor,lens,right) VALUES(?,?,?)', ((self._actor_id,uid,right) for right in ('move','read','write','execute')))
        world._audit(self._actor_id,None,'LENS_CREATED',{'uid':uid,'label':label,'kind':kind})

    @_atomic
    def connect(self, source, target, connection_id=None):
        self._auth()
        world = self._world
        connection = world._connection
        uid = _one(connection,'SELECT COALESCE(?,?) AS uid',(connection_id,'link_'+uuid4().hex))['uid']
        connection.execute('INSERT INTO connections(uid,source,target) VALUES(?,?,?)',(uid,source,target))
        world._audit(self._actor_id,None,'CONNECTED',{'uid':uid,'source':source,'target':target})
        return uid

    @_atomic
    def disconnect(self, connection_id):
        self._auth()
        world = self._world
        _one(world._connection,'UPDATE connections SET active=0 WHERE uid=? RETURNING uid',(connection_id,),'UNKNOWN_CONNECTION')
        world._audit(self._actor_id,None,'DISCONNECTED',{'uid':connection_id})

    @_atomic
    def actor(self, name, root='MASTER'):
        self._auth()
        world = self._world
        connection = world._connection
        _one(connection,'SELECT uid FROM lenses WHERE uid=? AND active=1',(root,),'UNKNOWN_LENS')
        actor,key=uuid4().hex,secrets.token_urlsafe(32)
        connection.execute('INSERT INTO actors(id,name,key_digest,root) VALUES(?,?,?,?)',(actor,name,_digest(key),root))
        connection.executemany('INSERT INTO grants(actor,lens,right) VALUES(?,?,?)',((actor,root,right) for right in ('move','read')))
        world._audit(self._actor_id,None,'ACTOR_CREATED',{'id':actor,'name':name,'root':root})
        return key

    @_atomic
    def grant(self, actor_key, lens_uid, rights=('move','read','write','execute')):
        self._auth()
        world = self._world
        connection = world._connection
        actor = world._actor(actor_key)
        selected = tuple(rights)
        connection.executemany('INSERT OR IGNORE INTO grants(actor,lens,right) VALUES(?,?,?)',((actor['id'],lens_uid,right) for right in selected))
        world._audit(self._actor_id,None,'GRANTED',{'actor':actor['id'],'lens':lens_uid,'rights':selected})

    @_atomic
    def revoke(self, actor_key, lens_uid, rights=('move','read','write','execute')):
        self._auth()
        world = self._world
        connection = world._connection
        actor = world._actor(actor_key)
        selected = tuple(rights)
        _one(connection,"SELECT 1 WHERE ? != ? OR NOT EXISTS(SELECT 1 FROM json_each(?) WHERE value='move')",
             (lens_uid,actor['root'],_canonical(selected)),'ROOT_ACCESS_REQUIRED')
        connection.executemany('DELETE FROM grants WHERE actor=? AND lens=? AND right=?',((actor['id'],lens_uid,right) for right in selected))
        world._audit(self._actor_id,None,'REVOKED',{'actor':actor['id'],'lens':lens_uid,'rights':selected})

    @_atomic
    def bookmark(self, actor_key, name, target_uid):
        self._auth()
        world = self._world
        actor = world._actor(actor_key)
        uid='bookmark_'+uuid4().hex
        connection = world._connection
        connection.execute('INSERT INTO bookmarks(uid,actor,name,target) VALUES(?,?,?,?)',(uid,actor['id'],name,target_uid))
        world._audit(self._actor_id,None,'BOOKMARK_CREATED',{'uid':uid,'actor':actor['id'],'name':name,'target':target_uid})
        return uid

    @_atomic
    def contract(self, descriptor):
        self._auth()
        from .execution import validate_binding
        binding = validate_binding(descriptor)
        world = self._world
        connection = world._connection
        connection.execute('INSERT INTO contracts(base_pin,common_action,inner_lens,unique_action,version,algorithm,input_type,descriptor) VALUES(?,?,?,?,?,?,?,?)',
                           tuple(binding[k] for k in ('BASE_PIN','COMMON_ACTION','INNER_LENS','UNIQUE_ACTION','version','algorithm','input_type'))+(_canonical(binding),))
        world._audit(self._actor_id,None,'CONTRACT_INSTALLED',binding)


class Zoombar:
    """Only public movement/data/execution gateway; contains no LENS objects."""
    def __init__(self, world, credential, session):
        actor=world._actor(credential)
        self._world, self._actor_id, self._session_id = world, actor['id'], session
        self._credential_digest=_digest(credential)

    @property
    def session_id(self):
        return self._session_id

    def _auth(self):
        world = self._world
        return _one(world._connection,'SELECT 1 FROM sessions s JOIN actors a ON a.id=s.actor WHERE s.id=? AND a.id=? AND a.key_digest=? AND a.active=1',(self._session_id,self._actor_id,self._credential_digest),'SESSION_FORBIDDEN')

    def _here(self):
        world = self._world
        return _one(world._connection,'SELECT lens FROM frames WHERE session=? ORDER BY position DESC LIMIT 1',(self._session_id,))['lens']

    def _permission(self, right):
        world = self._world
        connection = world._connection
        prefix=_one(connection,_VALID_PREFIX,{'session':self._session_id,'actor':self._actor_id})['length']
        _one(connection,'SELECT 1 WHERE ?=(SELECT COUNT(*) FROM frames WHERE session=?)',(prefix,self._session_id),'INVALID_PATH')
        return _one(world._connection,'SELECT 1 FROM grants g JOIN lenses l ON l.uid=g.lens WHERE g.actor=? AND g.lens=? AND g.right=? AND l.active=1',
                    (self._actor_id,self._here(),right),'ACCESS_DENIED')

    @_atomic
    def identity(self):
        self._auth()
        world = self._world
        actor = dict(_one(world._connection,'SELECT id,name,role FROM actors WHERE id=?',(self._actor_id,)))
        actor['session_id']=self._session_id
        return actor

    @_atomic
    def here(self):
        self._auth()
        return self._here()

    @_atomic
    def path(self):
        self._auth()
        world = self._world
        connection=world._connection
        return [row['lens'] for row in connection.execute('SELECT lens FROM frames WHERE session=? ORDER BY position',(self._session_id,))]

    @_atomic
    def see(self):
        self._auth()
        world = self._world
        connection = world._connection
        return [dict(row) for row in connection.execute('''
          SELECT l.uid,l.label,l.kind,c.uid AS connection_id FROM connections c JOIN lenses l ON l.uid=c.target
          JOIN lenses src ON src.uid=c.source
          JOIN grants gs ON gs.actor=? AND gs.lens=src.uid AND gs.right='move'
          JOIN grants gt ON gt.actor=gs.actor AND gt.lens=l.uid AND gt.right='move'
          WHERE c.source=? AND c.active=1 AND l.active=1 AND src.active=1 ORDER BY c.ordinal,c.uid
        ''',(self._actor_id,self._here()))]

    @_atomic
    def zoom_in(self, uid, connection_id=None):
        self._auth()
        world = self._world
        connection = world._connection
        prefix=_one(connection,_VALID_PREFIX,{'session':self._session_id,'actor':self._actor_id})['length']
        _one(connection,'SELECT 1 WHERE ?=(SELECT COUNT(*) FROM frames WHERE session=?)',(prefix,self._session_id),'INVALID_PATH')
        edge=_one(connection,'''SELECT c.uid FROM connections c JOIN lenses l ON l.uid=c.target
          JOIN grants g ON g.lens=c.target AND g.actor=? AND g.right='move'
          WHERE c.source=? AND c.target=? AND c.active=1 AND l.active=1
          AND (? IS NULL OR c.uid=?) ORDER BY c.ordinal,c.uid LIMIT 1''',
          (self._actor_id,self._here(),uid,connection_id,connection_id),'NOT_IN_LIST')
        connection.execute('INSERT INTO frames(session,position,lens,entry) SELECT ?,COUNT(*),?,? FROM frames WHERE session=?',
                           (self._session_id,uid,edge['uid'],self._session_id))
        world._audit(self._actor_id,self._session_id,'ZOOM_IN',{'to':uid,'connection_id':edge['uid']})

    @_atomic
    def zoom_out(self):
        self._auth()
        world = self._world
        connection = world._connection
        prefix=_one(connection,_VALID_PREFIX,{'session':self._session_id,'actor':self._actor_id})['length']
        count=_one(connection,'SELECT COUNT(*) AS n FROM frames WHERE session=?',(self._session_id,))['n']
        result=_one(connection,'''SELECT 'ROOT' AS mode,1 AS length WHERE :count=1
          UNION ALL SELECT 'ENTRY',:count-1 WHERE :count>1 AND :prefix=:count
          UNION ALL SELECT 'SAFE_RETURN',MAX(1,:prefix) WHERE :count>1 AND :prefix<:count''',{'count':count,'prefix':prefix})
        connection.execute('DELETE FROM frames WHERE session=? AND position>=?',(self._session_id,result['length']))
        world._audit(self._actor_id,self._session_id,'ZOOM_OUT',{'mode':result['mode'],'at':self._here(),'reason':dict(_one(connection,"SELECT 'ENTRY_EDGE_GONE' AS reason WHERE ?='SAFE_RETURN' UNION ALL SELECT NULL WHERE ?!='SAFE_RETURN'",(result['mode'],result['mode'])))['reason']})
        return result['mode']

    @_atomic
    def zoom_root(self):
        self._auth()
        world = self._world
        connection = world._connection
        connection.execute('DELETE FROM frames WHERE session=? AND position>0',(self._session_id,))
        world._audit(self._actor_id,self._session_id,'ZOOM_ROOT',{'at':self._here()})

    def walk(self, url):
        parsed=urlsplit(url)
        raw_path=parsed.path
        clean_path=raw_path.strip('/')
        parts=tuple(map(unquote,clean_path.split('/')))
        world = self._world
        lock=world._lock
        connection=world._connection
        with lock:
            self._auth()
            root=_one(connection,'SELECT root FROM sessions WHERE id=?',(self._session_id,))['root']
            _one(connection,"SELECT 1 WHERE ?='zoom' AND ?='world' AND ?='' AND ?='' AND ?=?",(parsed.scheme,parsed.netloc,parsed.query,parsed.fragment,parts[0],root),'BAD_URL')
            self.zoom_root()
            for uid in parts[1:]:
                self.zoom_in(uid)

    @_atomic
    def url(self):
        self._auth()
        world=self._world
        connection=world._connection
        parts=[row['lens'] for row in connection.execute('SELECT lens FROM frames WHERE session=? ORDER BY position',(self._session_id,))]
        return 'zoom://world/'+'/'.join(quote(part,safe='') for part in parts)

    @_atomic
    def bookmarks(self):
        self._auth()
        world=self._world
        connection=world._connection
        return [dict(row) for row in connection.execute('SELECT uid,name,name AS label,target FROM bookmarks WHERE actor=? ORDER BY name',(self._actor_id,))]

    def bookmark(self, name):
        world=self._world
        lock=world._lock
        connection=world._connection
        with lock:
            self._auth()
            target=_one(connection,'SELECT target FROM bookmarks WHERE actor=? AND (name=? OR uid=?)',(self._actor_id,name,name),'UNKNOWN_BOOKMARK')['target']
            start=self._here()
            row=_one(connection,'''WITH RECURSIVE reach(at,trail,depth) AS (
              SELECT ?,char(31)||?||char(31),0
              UNION ALL SELECT c.target,r.trail||c.target||char(31),r.depth+1
              FROM reach r JOIN connections c ON c.source=r.at AND c.active=1
              JOIN lenses l ON l.uid=c.target AND l.active=1
              JOIN grants g ON g.actor=? AND g.lens=c.target AND g.right='move'
              WHERE r.depth<64 AND instr(r.trail,char(31)||c.target||char(31))=0 LIMIT 10000
            ) SELECT trail FROM reach WHERE at=? ORDER BY depth,trail LIMIT 1''',(start,start,self._actor_id,target),'NO_ROUTE')
            parts=row['trail'].split(chr(31))[1:-1]
            for uid in parts[1:]:
                self.zoom_in(uid)

    @_atomic
    def put(self, value):
        self._auth()
        self._permission('write')
        world=self._world
        connection=world._connection
        body=_canonical(value)
        _one(connection,'SELECT 1 WHERE length(CAST(? AS BLOB))<=1048576',(body,),'DATA_TOO_LARGE')
        owner=self._here()
        digest='zc1:'+_digest(owner+'\0'+body)
        connection.execute('INSERT OR IGNORE INTO objects(hash,owner,body,created) VALUES(?,?,?,?)',(digest,owner,body,_now()))
        world._audit(self._actor_id,self._session_id,'DATA_PUT',{'owner':owner,'hash':digest})
        return digest

    @_atomic
    def read(self, hash):
        self._auth()
        self._permission('read')
        world=self._world
        row=_one(world._connection,'SELECT body FROM objects WHERE hash=? AND owner=?',(hash,self._here()),'FOREIGN_OR_UNKNOWN_HASH')
        return json.loads(row['body'])

    @_atomic
    def run(self, parameter_hash):
        self._auth()
        self._permission('execute')
        self._permission('read')
        self._permission('write')
        from .execution import evaluate
        world=self._world
        connection=world._connection
        here=self._here()
        row=_one(connection,'SELECT body FROM objects WHERE hash=? AND owner=?',(parameter_hash,here),'FOREIGN_OR_UNKNOWN_HASH')
        request=json.loads(row['body'])
        _one(connection,"SELECT 1 WHERE json_type(?)='object' AND json_extract(?,'$.INNER_LENS')=?",(row['body'],row['body'],here),'INNER_NOT_HERE')
        _one(connection,"SELECT 1 FROM frames WHERE session=? AND lens=json_extract(?,'$.BASE_PIN') LIMIT 1",(self._session_id,row['body']),'BASE_PIN_NOT_IN_PATH')
        binding=_one(connection,'''SELECT descriptor FROM contracts WHERE base_pin=json_extract(?,'$.BASE_PIN')
          AND common_action=json_extract(?,'$.COMMON_ACTION') AND inner_lens=?
          AND unique_action=json_extract(?,'$.UNIQUE_ACTION') ORDER BY version DESC LIMIT 1''',
          (row['body'],row['body'],here,row['body']),'NO_CONTRACT')
        descriptor=json.loads(binding['descriptor'])
        value=evaluate(request,descriptor)
        body=_canonical({'result':value,'contract_version':descriptor['version'],'parameter_hash':parameter_hash})
        digest='zc1:'+_digest(here+'\0'+body)
        connection.execute('INSERT OR IGNORE INTO objects(hash,owner,body,created) VALUES(?,?,?,?)',(digest,here,body,_now()))
        world._audit(self._actor_id,self._session_id,'CYCLE_DONE',{'parameter_hash':parameter_hash,'result_hash':digest,'contract_version':descriptor['version'],'INNER_LENS':here})

    @_atomic
    def events(self, limit=50):
        self._auth()
        world=self._world
        connection=world._connection
        count=_one(connection,'SELECT MIN(500,MAX(1,?)) AS n',(limit,),'BAD_INPUT')['n']
        return [dict(row,body=json.loads(row['body'])) for row in connection.execute('SELECT * FROM events WHERE actor=? ORDER BY sequence DESC LIMIT ?',(self._actor_id,count))]

    def history(self, limit=30):
        return self.events(limit)

    @_atomic
    def contracts(self):
        self._auth()
        self._permission('read')
        world=self._world
        connection=world._connection
        return [json.loads(row['descriptor']) for row in connection.execute('SELECT descriptor FROM contracts WHERE inner_lens=? ORDER BY unique_action,version',(self._here(),))]
