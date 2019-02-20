import dbm
import fcntl
import json
import six

db_fname_base = 'id'

class _DB:

    def __init__(self, write_flag=False, block_flag=True):
        self.write_flag = write_flag
        self.block_flag = block_flag
        self.db = dbm.open(db_fname_base, 'c')
        self.fo = open('%s.db' % db_fname_base)
        if self.write_flag:
            fcntl_flags = fcntl.LOCK_EX
        else:
            fcntl_flags = fcntl.LOCK_SH
        if not self.block_flag:
            fcntl_flags |= fcntl.LOCK_NB
        fcntl.flock(self.fo.fileno(), fcntl_flags)
        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()
        return False

    def __getitem__(self, key):
        return json.loads(self.db[key.encode('utf-8')].decode('utf-8'))

    def __setitem__(self, key, value):
        self.db[key.encode('utf-8')] = json.dumps(value).encode('utf-8')
        return

    def __delitem__(self, key):
        del self.db[key.encode('utf-8')]
        return

    def __iter__(self):
        for key in self.db.keys():
            yield key.decode('utf-8')
        return

    def close(self):
        self.db.close()
        self.fo.close()
        return

    def keys(self):
        return list(self)

class Identifier:

    def __init__(self, type, ident):
        if not isinstance(type, six.string_types):
            raise TypeError('type must be a string')
        if not isinstance(ident, six.string_types):
            raise TypeError('ident must be a string')
        self.type = type.lower()
        self.ident = ident
        self.key = '%s:%s' % (self.type, self.ident)
        return

    @classmethod
    def from_key(cls, key):
        if not isinstance(key, six.string_types):
            raise TypeError('key must be a string')
        parts = key.split(':', 1)
        if len(parts) == 1:
            raise ValueError('key must be of form "type:ident"')
        (type, ident) = parts
        return cls(type, ident)

    def __repr__(self):
        return "Identifier('%s', '%s')" % (self.type, self.ident)

    def __str__(self):
        return '%s:%s' % (self.type, self.ident)

    def __eq__(self, other):
        return self.type == other.type and self.ident == other.ident

    def __hash__(self):
        return hash(self.type + self.ident)

def link(i1, i2, asserter):
    if not isinstance(i1, Identifier) or not isinstance(i2, Identifier):
        raise TypeError('identifiers must be Identifier instances')
    if not isinstance(asserter, six.string_types):
        raise TypeError('asserter must be a string')
    if i1 == i2:
        raise ValueError('identifiers are the same')
    with _DB(write_flag=True) as db:
        _link(db, i1, i2, asserter)
        _link(db, i2, i1, asserter)
    return

def _link(db, i1, i2, asserter):
    try:
        d = db[i1.key]
    except KeyError:
        d = {}
    asserters = d.setdefault(i2.key, [])
    if asserter not in asserters:
        asserters.append(asserter)
    db[i1.key] = d
    return

def unlink(i1, i2, asserter):
    if not isinstance(i1, Identifier) or not isinstance(i2, Identifier):
        raise TypeError('identifiers must be Identifier instances')
    if not isinstance(asserter, six.string_types):
        raise TypeError('asserter must be a string')
    if i1 == i2:
        raise ValueError('identifiers are the same')
    with _DB(write_flag=True) as db:
        _unlink(db, i1, i2, asserter)
        _unlink(db, i2, i1, asserter)
    return

def _unlink(db, i1, i2, asserter):
    try:
        d = db[i1.key]
    except KeyError:
        return
    if i2.key not in d:
        return
    if asserter not in d[i2.key]:
        return
    d[i2.key].remove(asserter)
    if not d[i2.key]:
        del d[i2.key]
    if d:
        db[i1.key] = d
    else:
        del db[i1.key]
    return

def get_links(i):
    if not isinstance(i, Identifier):
        raise TypeError('identifier must be an Identifier instances')
    with _DB() as db:
        try:
            d0 = db[i.key]
        except KeyError:
            d0 = {}
    d = {}
    for (key, asserters) in d0.items():
        d[Identifier.from_key(key)] = set(asserters)
    return d

# eof
