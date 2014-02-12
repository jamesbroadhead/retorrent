
import unittest

from retorrentlib.braced import extract_checksum, is_checksum, remove_braces

class TestBraced(unittest.TestCase):
    def test_remove_braces(self):
        self.assertEqual(remove_braces('foo.bar.(what).zamf'), 'foo.bar.zamf')
        self.assertEqual(remove_braces('foo.bar.(w(h)at).zamf'), 'foo.bar.zamf')
        self.assertEqual(remove_braces('The Band - Let Me Out - 1993 (Vinyl - MP3 - V0 (VBR)) (1).torrent'), 'The.Band.-.Let.Me.Out.-.1993.torrent')

    @unittest.skip("need to mock some stuff... goes interactive :(")
    def test_remove_braces_BROKEN(self):
        self.assertEqual(remove_braces('Able Baker [1981].mkv'), 'Able.Baker.1981.mkv')
        self.assertEqual(remove_braces('[able].baker.charlie.S2...01.[720p.H264][AAAAAAAA].mkv'), 'baker.charlie.S2.01.[AAAAAAAA].mkv')

        self.assertEqual(remove_braces('[able].baker.charlie.S2...01.[720p.H264][AAAAAAAA].mkv', preserve_checksum=False), 'baker.charlie.S2.01.mkv')

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
        self.assertEqual(is_checksum(u'halleo'), False)
        self.assertEqual(is_checksum('8888888'), False)
        self.assertEqual(is_checksum('888888888'), False)
        self.assertEqual(is_checksum('[88888888]'), True)
        self.assertEqual(is_checksum('(88888888)'), True)
        self.assertEqual(is_checksum(u'88888888'), True)
        self.assertEqual(is_checksum(u'R8888888'), False)
        self.assertEqual(is_checksum(u'[88888888]'), True)
        self.assertEqual(is_checksum(u'[R8888888]'), False)
