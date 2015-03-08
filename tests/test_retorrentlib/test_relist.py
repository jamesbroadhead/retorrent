""" test_retorrentlib.test_relist """

import unittest

from retorrentlib.relist import lowercase_non_checksums

class TestLowerCasing(unittest.TestCase): # pylint: disable=too-many-public-methods

    def test_lowercasing(self):
        self.assertEqual(lowercase_non_checksums(['foo', 'bar', 'baz']), ['foo', 'bar', 'baz'])
        self.assertEqual(lowercase_non_checksums(['FOO', 'BAR', 'BAZ']), ['foo', 'bar', 'baz'])
        self.assertEqual(lowercase_non_checksums(['foo', 'BAR', 'baz']), ['foo', 'bar', 'baz'])

        self.assertEqual(lowercase_non_checksums(['foo', 'AAAAAAAA', 'baz']),
                         ['foo', 'AAAAAAAA', 'baz'])

        self.assertEqual(lowercase_non_checksums(['foo', '[AAAAAAAA]', 'baz']),
                         ['foo', '[AAAAAAAA]', 'baz'])
