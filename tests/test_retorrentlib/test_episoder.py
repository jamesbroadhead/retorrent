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

class EpisoderTestMixin(object):
    def setUp(self):
        self.e = Episoder()

        # set interactive, but explode if we hit those branches
        self.e.interactive = True
        self.e.booloptionator = raise_exception
        self.e.optionator = raise_exception

class TestConvertIfEpisodeNumber(EpisoderTestMixin, unittest.TestCase):

    def test_single_file_movies_noninteractive(self):
        self.e.is_movie = True
        self.e.num_interesting_files = 1

        filename_split = [u'able', u'baker', u'charlie', u'1989', u'1', u'mkv']

        expected = None
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 1), expected)

    def test_episode_conversion_with_literal_episode(self):
        filename_split = [u'the', u'alpha', u'episode', u'3', u'mkv']
        expected = ([u'the', u'alpha', u's01e03', 'mkv'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 2), expected)

    def test_episode_conversion_with_literal_pilot(self):
        filename_split = [u'the', u'alpha', u'pilot', u'mkv']
        expected = ([u'the', u'alpha', u's00e00', 'mkv'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 2), expected)

    def test_convert_for_single_digit(self):
        filename_split = [u'5']
        expected = ([u's01e05'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)

    def test_convert_for_single_digit_doubleitem(self):
        filename_split = [u'1', u'03']
        expected = ([u's01e03'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)

    def test_convert_for_number_divider_number(self):
        filename_split = [u'9x03']
        expected = ([u's09e03'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)
