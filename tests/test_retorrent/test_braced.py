""" tests for retorrent.braced """

from datetime import datetime
import unittest

from retorrent.braced import extract_checksum, is_checksum, is_year, remove_braces

class TestBraced(unittest.TestCase): # pylint: disable=too-many-public-methods
    def test_remove_braces(self):
        self.assertEqual(remove_braces('foo.bar.(what).zamf'), 'foo.bar.zamf')
        self.assertEqual(remove_braces('foo.bar.(w(h)at).zamf'), 'foo.bar.zamf')
        self.assertEqual(
            remove_braces('The Band - Let Me Out - 1993 (Vinyl - MP3 - V0 (VBR)) (1).torrent'),
            'The.Band.-.Let.Me.Out.-.1993.torrent')

    def test_remove_braces_BROKEN(self):
        self.assertEqual(remove_braces('Able Baker [1981].mkv'), 'Able.Baker.1981.mkv')
        self.assertEqual(
            remove_braces('[able].baker.charlie.S2...01.[720p.H264][AAAAAAAA].mkv'),
            'baker.charlie.S2.01.[AAAAAAAA].mkv')

        self.assertEqual(
            remove_braces('[able].baker.charlie.S2...01.[720p.H264][AAAAAAAA].mkv',
                          preserve_checksum=False),
            'baker.charlie.S2.01.mkv')

    def test_extract_checksum(self):
        self.assertEqual(extract_checksum('[AAAAAAAA]'), '[AAAAAAAA]')
        self.assertEqual(extract_checksum('AAAAAAAA'), '[AAAAAAAA]')
        self.assertEqual(extract_checksum('[aaaaaaaa]'), '[AAAAAAAA]')
        self.assertEqual(extract_checksum('aaaaaaaa'), '[AAAAAAAA]')
        self.assertEqual(extract_checksum('foo.aaaaaaaa'), '[AAAAAAAA]')
        self.assertEqual(extract_checksum('aaaaaaaa.foo'), '[AAAAAAAA]')
        self.assertEqual(extract_checksum('foo.aaaaaaaa.bar'), '[AAAAAAAA]')
        self.assertEqual(extract_checksum('aaaaaaaa.bbbbbbbb'), '[AAAAAAAA]')
        self.assertEqual(extract_checksum('words.are.neat'), '')


    def test_is_checksum(self):
        self.assertEqual(is_checksum('88888888'), True)
        self.assertEqual(is_checksum('halleo'), False)
        self.assertEqual(is_checksum('halleo'), False)
        self.assertEqual(is_checksum('8888888'), False)
        self.assertEqual(is_checksum('888888888'), False)
        self.assertEqual(is_checksum('[88888888]'), True)
        self.assertEqual(is_checksum('(88888888)'), True)
        self.assertEqual(is_checksum('88888888'), True)
        self.assertEqual(is_checksum('R8888888'), False)
        self.assertEqual(is_checksum('[88888888]'), True)
        self.assertEqual(is_checksum('[R8888888]'), False)


    def test_is_year(self):
        self.assertEqual(is_year('2014', interactive=False), True)

        self.assertEqual(is_year('1939', interactive=False), False)
        self.assertEqual(is_year('1940', interactive=False), True)

        this_year = str(datetime.now().year)
        next_year = str(datetime.now().year + 1)
        self.assertEqual(is_year(this_year, interactive=False), True)
        self.assertEqual(is_year(next_year, interactive=False), False)

    def test_is_year_two_digits(self):
        self.assertEqual(is_year('14', interactive=False), False) # 1914
        self.assertEqual(is_year('99', interactive=False), True) # 1999
