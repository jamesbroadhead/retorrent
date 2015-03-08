""" tests for retorrentlib.episoder """

import unittest

from retorrentlib.episoder import Episoder
# pylint: disable=too-many-public-methods

class TestException(Exception):
    pass

def raise_exception(*args, **kwargs):
    #pylint: disable=unused-argument
    raise TestException('unexpected call!')


class TestEpisoder(unittest.TestCase):

    def test_is_good_epno(self):
        self.assertTrue(Episoder.is_good_epno('s01e01'))
        self.assertTrue(Episoder.is_good_epno('s01e010'))
        self.assertFalse(Episoder.is_good_epno('e01'))
        self.assertFalse(Episoder.is_good_epno('ep01'))
        self.assertTrue(Episoder.is_good_epno('cd01'))
        self.assertTrue(Episoder.is_good_epno('op01'))
        self.assertTrue(Episoder.is_good_epno('ed01'))

class TestConvertIfEpisodeNumber(unittest.TestCase):

    def setUp(self):
        self.e = Episoder()
        self.e.booloptionator = raise_exception

    def test_single_file_movies_noninteractive(self):
        self.e.interactive = True
        self.e.is_movie = True
        self.e.num_interesting_files = 1

        filename_split = [u'able', u'baker', u'charlie', u'1989', u'1', u'mkv']
        expected = (filename_split, False)

        self.assertEqual(self.e.convert_if_episode_number(filename_split, 1, True),
                         expected)
