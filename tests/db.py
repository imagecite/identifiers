import os
import dbm
import select
import signal
import identifiers
from .common import BaseTestWithEmptyDB

class BaseTestWithEmptyOpenDB(BaseTestWithEmptyDB):

    """create an empty database file and open it"""

    def setUp(self):
        BaseTestWithEmptyDB.setUp(self)
        self.db = identifiers._DB()
        return

    def tearDown(self):
        BaseTestWithEmptyDB.tearDown(self)
        self.db.close()
        return

class BaseTestWithSimpleDB(BaseTestWithEmptyOpenDB):

    """create a database file with one entry and open it"""

    def setUp(self):
        BaseTestWithEmptyOpenDB.setUp(self)
        self.value = {'b': 'c'}
        self.db['a'] = self.value
        return

class TestDBEmpty(BaseTestWithEmptyOpenDB):

    def test_keys(self):
        self.assertEqual(self.db.keys(), [])
        return

    def test_key(self):
        with self.assertRaises(KeyError):
            self.db['a']
        return

    def test_in(self):
        self.assertFalse('a' in self.db)
        return

class TestDBValue(BaseTestWithSimpleDB):

    def test_keys(self):
        self.assertEqual(self.db.keys(), ['a'])
        return

    def test_value(self):
        self.assertEqual(self.db['a'], self.value)
        return
        
    def test_in(self):
        self.assertTrue('a' in self.db)
        return

    def test_del(self):
        del self.db['a']
        self.assertEqual(self.db.keys(), [])

class BaseTestShared(BaseTestWithEmptyDB):

    """create an empty database file and a second process with the database 
    open"""

    def setUp(self):
        BaseTestWithEmptyDB.setUp(self)
        (r_fo, w_fo) = os.pipe()
        self.pid = os.fork()
        if self.pid == 0:
            os.close(r_fo)
            db = identifiers._DB()
            os.write(w_fo, b'ok')
            select.select([], [], [], 10)
            os.close(w_fo)
            os._exit()
        else:
            select.select([r_fo], [], [])
            os.close(r_fo)
            os.close(w_fo)
        return

    def tearDown(self):
        BaseTestWithEmptyDB.tearDown(self)
        os.kill(self.pid, signal.SIGTERM)
        os.wait()
        return

class TestDBBlocking(BaseTestShared):

    def test_shared(self):
        try:
            db = identifiers._DB()
        except:
            self.fail()
        finally:
            db.close()
        return

    def test_exclusive(self):
        with self.assertRaisesRegexp(IOError, 
                                     'Resource temporarily unavailable'):
            db = identifiers._DB(write_flag=True, block_flag=False)
        return

# eof
