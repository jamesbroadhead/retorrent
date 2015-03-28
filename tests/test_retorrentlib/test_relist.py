""" test_retorrentlib.test_relist """

import unittest

from retorrentlib.relist import lowercase_non_checksums, replace_singleitem, replace_doubleitem

class TestLowerCasing(unittest.TestCase): # pylint: disable=too-many-public-methods

    def test_lowercasing(self):
        self.assertEqual(lowercase_non_checksums(['foo', 'bar', 'baz']), ['foo', 'bar', 'baz'])
        self.assertEqual(lowercase_non_checksums(['FOO', 'BAR', 'BAZ']), ['foo', 'bar', 'baz'])
        self.assertEqual(lowercase_non_checksums(['foo', 'BAR', 'baz']), ['foo', 'bar', 'baz'])

        self.assertEqual(lowercase_non_checksums(['foo', 'AAAAAAAA', 'baz']),
                         ['foo', 'AAAAAAAA', 'baz'])

        self.assertEqual(lowercase_non_checksums(['foo', '[AAAAAAAA]', 'baz']),
                         ['foo', '[AAAAAAAA]', 'baz'])

class TestReplacement(unittest.TestCase):
    _input = [ str(i) for i in range(6) ]

    def test_replace_singleitem(self):
        expected = ['0', '1', 'fox', '3', '4', '5']
        self.assertEqual(replace_singleitem(self._input, 2, 'fox'), expected)

    def test_replace_doubleitem(self):
        expected = ['0', '1', 'fox', '4', '5']
        self.assertEqual(replace_doubleitem(self._input, 2, 'fox'), expected)

    def test_single_item_list(self):
        expected = ['fox']
        self.assertEqual(replace_singleitem(['asdf'], 0, 'fox'), expected)

    def test_multireplace_near_bounds(self):
        expected = ['0', '1', '2', '3', '4', 'fox' ]
        self.assertEqual(replace_doubleitem(self._input, 5, 'fox'), expected)

        expected = ['fox', '2', '3', '4', '5' ]
        self.assertEqual(replace_doubleitem(self._input, 0, 'fox'), expected)
