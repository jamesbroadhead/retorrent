import unittest

from retorrentlib.episoder import Episoder

class TestEpisoder(unittest.TestCase):

    def test_is_good_epno(self):
        self.assertTrue(Episoder.is_good_epno('s01e01'))
        self.assertTrue(Episoder.is_good_epno('s01e010'))
        self.assertFalse(Episoder.is_good_epno('e01'))
        self.assertFalse(Episoder.is_good_epno('ep01'))
        self.assertTrue(Episoder.is_good_epno('cd01'))
        self.assertTrue(Episoder.is_good_epno('op01'))
        self.assertTrue(Episoder.is_good_epno('ed01'))
