"""
tests for engname
"""
import unittest

from hypothesis import given
from hypothesis.strategies import lists, text

from retorrent.restring import endottables
from retorrent.engname import removables, replace_chars, to_storage_name

#pylint: disable=too-many-public-methods
class TestToStorageName(unittest.TestCase):

    @given(text(alphabet=['"', "'", '.']))
    def test_removal(self, s):
        self.assertEqual(to_storage_name(s), '')

    @given(text())
    def test_replacement(self, s):
        output = to_storage_name(s)
        self.assertNotIn('..', output)
        j = 0

        if output == '':
            self.assertTrue(set(s) <= set(removables + endottables + ['.']))
            return

        for c in s:
            if c in removables or (c in endottables + ['.'] and (
                        j == 0 or j == len(output))):
                # removables get removed - should not compare
                # leading and trailing dots also get removed
                continue
            elif c in endottables + ['.']:
                # either the current should be dot or the prev should be
                if output[j] == '.':
                    j += 1
                else:
                    self.assertEqual(output[j-1], '.')
                    # do not increment j, we haven't moved on yet
            else:
                self.assertEqual(output[j], c.lower(),
                    'from %r got %r removing %r and %r[%r] != %r' % (
                    s, output, removables, output, j, c))
                j += 1



class TestReplaceChars(unittest.TestCase):
    @given(text(), lists(elements=text(max_size=1)))
    def test_removal(self, s, chars):
        output = replace_chars(s, chars, '')

        replace_set = set(chars)
        j = 0
        for c in s:
            if c in replace_set:
                continue
            else:
                self.assertEqual(output[j], c, '%r %r %r %r' % (
                    output, replace_set, c, c in replace_set))
                j += 1

    @given(text(), lists(elements=text(max_size=1)),
            text(min_size=1, max_size=1))
    def test_replacement(self, s, chars, replace_with):
        output = replace_chars(s, chars, replace_with)

        replace_set = set(chars)
        j = 0
        for c in s:
            if c in replace_set:
                self.assertEqual(output[j], replace_with)
            else:
                self.assertEqual(output[j], c,
                    'from %r got %r removing %r and %r != %r' % (
                    s, output, replace_set, output[j], c))
            j += 1
