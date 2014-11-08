""" tests for retorrentlib.restring """

import unittest

from retorrentlib.restring import endot

class TestDotting(unittest.TestCase): # pylint: disable=too-many-public-methods

    def test_endot(self):
        self.assertEqual(endot('Able Baker.1981..mkv'), 'Able.Baker.1981.mkv')

        self.assertEqual(endot('baker.charlie.S2...01.[AAAAAAAA]..mkv'),
                         'baker.charlie.S2.01.[AAAAAAAA].mkv')
        self.assertEqual(endot('.baker.charlie.S2...01..mkv.'), 'baker.charlie.S2.01.mkv')
