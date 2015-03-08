""" test_retorrentlib.test_filenamer """
import unittest

from retorrentlib.filenamer import Filenamer

# pylint: disable=too-many-public-methods

class TestApplyRemoveSetOnFilename(unittest.TestCase):

    def test_empty_removeset(self):
        filename_split = ['foo', 'bar', 'baz']
        res = Filenamer.apply_removeset(filename_split, {}, False)
        self.assertEqual(res, filename_split)

    def test_basic_removal(self):
        filename_split = ['foo', 'bar', 'baz']
        res = Filenamer.apply_removeset(filename_split, {'bar'}, False)
        self.assertEqual(res, ['foo', 'baz'])

    def test_final_element_in_removeset(self):
        filename_split = ['foo', 'bar', 'baz']
        res = Filenamer.apply_removeset(filename_split, {'baz'}, False)
        self.assertEqual(res, filename_split)

class TestApplyRemoveSetOnFoldername(unittest.TestCase):

    def test_empty_removeset(self):
        filename_split = ['foo', 'bar', 'baz']
        res = Filenamer.apply_removeset(filename_split, {}, True)
        self.assertEqual(res, filename_split)

    def test_basic_removal(self):
        filename_split = ['foo', 'bar', 'baz']
        res = Filenamer.apply_removeset(filename_split, {'bar'}, True)
        self.assertEqual(res, ['foo', 'baz'])

    def test_final_element_in_removeset(self):
        filename_split = ['foo', 'bar', 'baz']
        res = Filenamer.apply_removeset(filename_split, {'baz'}, True)
        self.assertEqual(res, filename_split[0:2])
