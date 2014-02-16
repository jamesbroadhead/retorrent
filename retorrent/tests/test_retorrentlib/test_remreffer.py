
import unittest

from retorrentlib.remreffer import uniq

class TestUniq(unittest.TestCase):

    def test_uniq(self):
        i = [ 1, 1, 2, 3, 2, 3, 4, 5, 3, 4, 5 ]
        self.assertEqual(uniq(i), [1, 2, 3, 4, 5])

