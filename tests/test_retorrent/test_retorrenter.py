import unittest

from retorrent.retorrenter import Retorrenter

class StubConfig(object):
    ''' This should evolve to:
    - contain the same info as the default config file (consistency)
    - should move into the codebase (consistency)
    - the default config file should be generated from it (consistency, flexibility)
    '''
    configdir = ''
    global_conf = { 'ignore_if_in_path': ['extras'] }
    categories = {}
    filetype_definitions = {}
    divider_symbols = {}


#pylint: disable=too-many-public-methods
class TestRetorrenter(unittest.TestCase):

    def setUp(self):
        self.r = Retorrenter(StubConfig())


    def test_is_of_interest_if_intermeds_should_be_ignored(self):
        self.assertEqual(False,
            self.r.is_of_interest('/a/TARGET/Extras/some_extra.mkv', 'Extras', 'some_extra.mkv'))
