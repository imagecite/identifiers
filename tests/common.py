import unittest
import os
import identifiers

test_db_base = 'test'
test_db_fname = '%s.db' % test_db_base

class BaseTestWithEmptyDB(unittest.TestCase):

    """create an empty database file but don't open it"""

    def setUp(self):
        if os.path.exists(test_db_fname):
            os.unlink(test_db_fname)
        identifiers.db_fname_base = test_db_base
        return

    def tearDown(self):
        if os.path.exists(test_db_fname):
            os.unlink(test_db_fname)
        return

# eof
