""" tests for test_retorrentlib.test_restring """

import unittest

from retorrentlib.restring import endot, remove_camelcase

class TestDotting(unittest.TestCase): # pylint: disable=too-many-public-methods

    def test_endot(self):
        self.assertEqual(endot('Able Baker.1981..mkv'), 'Able.Baker.1981.mkv')

        self.assertEqual(endot('baker.charlie.S2...01.[AAAAAAAA]..mkv'),
                         'baker.charlie.S2.01.[AAAAAAAA].mkv')
        self.assertEqual(endot('.baker.charlie.S2...01..mkv.'), 'baker.charlie.S2.01.mkv')

class TestCamelCase(unittest.TestCase): # pylint: disable=too-many-public-methods
    def test_remove_camelcase(self):
        self.assertEqual('', remove_camelcase(''))

        self.assertEqual('foo', remove_camelcase('foo'))

        self.assertEqual('foo.bar', remove_camelcase('fooBar'))
