from StringIO import StringIO
import unittest

from mock import patch

from retorrent.entry_points.find_tfile import _main as find_tfile_main

#pylint: disable=too-many-public-methods
class TestEpisoder(unittest.TestCase):

    @patch("retorrent.entry_points.find_tfile._get_results")
    def test_main_prints_space_delimited_filenames(self, mock_get_results):
        result = [ 'a', 'b' ]
        mock_get_results.return_value = result
        expected = ' '.join(result)

        my_stdout = StringIO()
        find_tfile_main('', '', out=my_stdout)
        output = my_stdout.getvalue().strip()

        self.assertEqual(output, expected)
