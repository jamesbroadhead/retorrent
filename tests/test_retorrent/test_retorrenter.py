import unittest

from retorrent.retorrenter import Retorrenter

#pylint: disable=too-many-public-methods
class TestRetorrenter(unittest.TestCase):

    def setUp(self):
        self.r = Retorrenter()



    def test_is_of_interest_if_intermeds_should_be_ignored(self):
        self.r.global_conf['ignore_if_in_path'] = ['extras']

        self.assertEqual(False,
            self.r.is_of_interest('/a/TARGET/Extras/some_extra.mkv', 'Extras', 'some_extra.mkv'))
