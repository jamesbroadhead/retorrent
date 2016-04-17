""" tests for retorrentlib.episoder """

import unittest

from mock import Mock

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

    def test_episodenumber_with_version(self):
        filename_split = [u'03v2']
        expected = ([u's01e03'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)

    def test_triple_digit_with_2_digit_epno(self):
        self.e.ask_for_digits_in_epno = Mock(return_value=2)

        filename_split = ['501']
        expected = ([u's05e01'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)

    def test_triple_digit_with_3_digit_epno(self):
        self.e.ask_for_digits_in_epno = Mock(return_value=3)

        filename_split = ['501']
        expected = ([u's01e501'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)

    def test_triple_digit_with_non_epno_sentinel(self):
        self.e.ask_for_digits_in_epno = Mock(return_value=self.e.NOT_AN_EPNO_SENTINEL)

        filename_split = ['501']
        expected = (None)
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)

    def test_letters_as_episode_numbers(self):
        self.e.ask_if_single_letter_is_epno = Mock(return_value=True)
        filename_split = ['sb']
        expected = (['s01e02'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)

    def test_letters_which_are_not_episode_numbers(self):
        self.e.ask_if_single_letter_is_epno = Mock(return_value=False)
        filename_split = ['sb']
        expected = (None)
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)

    def test_start_ident_single_item(self):
        filename_split = ['s01']
        expected = (['s01e01'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)

    def test_start_ident_doubleitem(self):
        filename_split = ['s01', 'e02']
        expected = (['s01e02'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)

    def test_start_ident_start_special(self):
        filename_split = ['op01']
        expected = (['op01'])
        self.assertEqual(self.e.convert_if_episode_number(filename_split, 0), expected)
