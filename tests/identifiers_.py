import unittest
import os
import identifiers
from .common import BaseTestWithEmptyDB

test_db_base = 'test'
test_db_fname = '%s.db' % test_db_base

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.i1 = identifiers.Identifier('a', 'b')
        self.i2 = identifiers.Identifier('a', 'b')
        self.i3 = identifiers.Identifier('a', 'c')
        self.i4 = identifiers.Identifier('A', 'b')
        return

class TestIdentifier(BaseTest):

    def test_str(self):
        self.assertEqual(str(self.i1), 'a:b')
        return

    def test_repr(self):
        self.assertEqual(repr(self.i1), "Identifier('a', 'b')")
        return

    def test_equal(self):
        self.assertEqual(self.i1, self.i2)
        return

    def test_hash_equal(self):
        self.assertEqual(hash(self.i1), hash(self.i2))
        return

    def test_not_equal(self):
        self.assertNotEqual(self.i1, self.i3)
        return

    def test_hash_not_equal(self):
        self.assertNotEqual(hash(self.i1), hash(self.i3))
        return

    def test_types(self):
        with self.assertRaises(TypeError):
            identifiers.Identifier(1, 'b')
        with self.assertRaises(TypeError):
            identifiers.Identifier('a', 2)
        return

    def test_case(self):
        self.assertEqual(self.i1, self.i4)
        return

    def test_from_key_type(self):
        with self.assertRaises(TypeError):
            identifiers.Identifier.from_key(1)
        return

    def test_from_key_value(self):
        with self.assertRaises(ValueError):
            identifiers.Identifier.from_key('a')
        return

    def test_from_key(self):
        i = identifiers.Identifier.from_key(self.i1.key)
        self.assertEquals(i, self.i1)
        return

    def test_from_key_case(self):
        i = identifiers.Identifier.from_key('A:b')
        self.assertEquals(i, self.i1)
        return

class TestLinksBasics(BaseTest):

    def test_link_types(self):
        with self.assertRaises(TypeError):
            identifiers.link(0, self.i2, 'ch')
        with self.assertRaises(TypeError):
            identifiers.link(self.i1, 0, 'ch')
        with self.assertRaises(TypeError):
            identifiers.link(self.i1, self.i3, 0)
        return

    def test_link_values(self):
        with self.assertRaises(ValueError):
            identifiers.link(self.i1, self.i2, 'ch')
        return

    def test_get_links_type(self):
        with self.assertRaises(TypeError):
            identifiers.get_links(0)
        return

    def test_get_links_return(self):
        self.assertEqual(identifiers.get_links(self.i1), {})
        return

    def test_unlink_types(self):
        with self.assertRaises(TypeError):
            identifiers.unlink(0, self.i2, 'ch')
        with self.assertRaises(TypeError):
            identifiers.unlink(self.i1, 0, 'ch')
        with self.assertRaises(TypeError):
            identifiers.unlink(self.i1, self.i3, 0)
        return

    def test_unlink_values(self):
        with self.assertRaises(ValueError):
            identifiers.unlink(self.i1, self.i2, 'ch')
        return

class BaseTestLinks(BaseTestWithEmptyDB):

    def setUp(self):
        BaseTestWithEmptyDB.setUp(self)
        self.i1 = identifiers.Identifier('a', 'b')
        self.i2 = identifiers.Identifier('a', 'c')
        identifiers.link(self.i1, self.i2, 'ch')
        return

class TestLinks(BaseTestLinks):

    def test_link(self):
        links = identifiers.get_links(self.i1)
        self.assertEquals(links.keys(), [self.i2])
        self.assertEquals(links[self.i2], {'ch'})
        links = identifiers.get_links(self.i2)
        self.assertEquals(links.keys(), [self.i1])
        self.assertEquals(links[self.i1], {'ch'})
        return

    def test_unlink(self):
        identifiers.unlink(self.i1, self.i2, 'ch')
        links = identifiers.get_links(self.i1)
        self.assertEqual(links, {})
        links = identifiers.get_links(self.i2)
        self.assertEqual(links, {})
        return

class TestLinksDuplicateAsserter(BaseTestLinks):

    def test_duplicate_asserter(self):
        identifiers.link(self.i1, self.i2, 'ch')
        self.assertEquals(identifiers.get_links(self.i1), {self.i2: {'ch'}})
        self.assertEquals(identifiers.get_links(self.i2), {self.i1: {'ch'}})
        return

class TestLinksAdditionalAsserter(BaseTestLinks):

    def setUp(self):
        BaseTestLinks.setUp(self)
        identifiers.link(self.i1, self.i2, 'jb')
        return

    def test_additional_asserter(self):
        asserters = {'ch', 'jb'}
        self.assertEquals(identifiers.get_links(self.i1), {self.i2: asserters})
        self.assertEquals(identifiers.get_links(self.i2), {self.i1: asserters})
        return

    def test_unlink(self):
        identifiers.unlink(self.i1, self.i2, 'ch')
        asserters = {'jb'}
        self.assertEquals(identifiers.get_links(self.i1), {self.i2: asserters})
        self.assertEquals(identifiers.get_links(self.i2), {self.i1: asserters})
        return

# eof
