""" test_retorrent.test_filenamer """
import unittest

from retorrent.filenamer import Filenamer

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

class TestDropFileExtension(unittest.TestCase):

    def setUp(self):
        self.fn = Filenamer(['.', '/'], { 'mkv': {} } )

    def test_returns_empty_list_on_empty_input(self):
        self.assertEqual(self.fn.drop_file_extension([]), [])
