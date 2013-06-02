#!/usr/bin/python
"""
Utility module for functions dealing with strings containing substrings inside braces

"""
from retorrentlib.restring import dotjoin, endot
from logdecorators.tracelogdecorator import tracelogdecorator

braces = {
    '[' : ']',
    '{' : '}',
    '(' : ')'
}
hexdigits = '0123456789abcdefABCDEF' + u'0123456789abcdefABCDEF'

@tracelogdecorator
def is_checksum(item):
    """
    >>> is_checksum('88888888')
    True

    >>> is_checksum('halleo')
    False

    >>> is_checksum(u'halleo')
    False

    >>> is_checksum('8888888')
    False

    >>> is_checksum('888888888')
    False

    >>> is_checksum('[88888888]')
    True

    >>> is_checksum('(88888888)')
    True

    >>> is_checksum(u'88888888')
    True

    >>> is_checksum(u'R8888888')
    False

    >>> is_checksum(u'[88888888]')
    True

    >>> is_checksum(u'[R8888888]')
    False
    """
    # 8-digit checksum + braces
    if len(item) == 10:
        if (not item[0] in braces or
                not item[-1] == braces.get(item[0], None)):
            return False
        item = item[1:-1]

    if not len(item) == 8:
        return False

    if set(item) <= set(hexdigits):
        return True
    return False


def extract_checksum(filename):
    """
    For a filename delimited by dots, return the first checksum
    >>> extract_checksum('[AAAAAAAA]')
    '[AAAAAAAA]'

    >>> extract_checksum('AAAAAAAA')
    '[AAAAAAAA]'

    >>> extract_checksum('[aaaaaaaa]')
    '[AAAAAAAA]'

    >>> extract_checksum('aaaaaaaa')
    '[AAAAAAAA]'

    >>> extract_checksum('foo.aaaaaaaa')
    '[AAAAAAAA]'

    >>> extract_checksum('aaaaaaaa.foo')
    '[AAAAAAAA]'

    >>> extract_checksum('foo.aaaaaaaa.bar')
    '[AAAAAAAA]'

    >>> extract_checksum('aaaaaaaa.bbbbbbbb')
    '[AAAAAAAA]'

    >>> extract_checksum('words.are.neat')
    ''
    """
    for segment in filename.split('.'):

        if is_checksum(segment):
            if len(segment) == 8:
                segment = '[%s]' % (segment)
            return segment.upper()
    return ''

@tracelogdecorator
def remove_braces(filename, preserve_checksum=True, remove_content=True):
    """
    Removes braces and internal content, with special rules for checksums
    Optionally preserves content, removing braces

    >>> remove_braces('foo.bar.(what).zamf', remove_content=False)
    'foo.bar.what.zamf'

    >>> remove_braces('foo.bar.(what).zamf', remove_content=True)
    'foo.bar.zamf'

    >>> remove_braces('foo.bar.(w(h)at).zamf', remove_content=False)
    'foo.bar.w.h.at.zamf'

    >>> remove_braces('foo.bar.(w(h)at).zamf', remove_content=True)
    'foo.bar.zamf'

    >>> remove_braces('foo.bar.what.(88888888).zamf', remove_content=False)
    'foo.bar.what.[88888888].zamf'

    >>> remove_braces('foo.bar.what.(aaaaaaaa).zamf', remove_content=False)
    'foo.bar.what.[AAAAAAAA].zamf'

    >>> remove_braces('foo.bar.what.(88888888).zamf', preserve_checksum=False)
    'foo.bar.what.zamf'

    >>> remove_braces('The Band - Let Me Out - 1993 (Vinyl - MP3 - V0 (VBR)) (1).torrent', remove_content=False)
    'The.Band.-.Let.Me.Out.-.1993.Vinyl.-.MP3.-.V0.VBR.1.torrent'

    >>> remove_braces('The Band - Let Me Out - 1993 (Vinyl - MP3 - V0 (VBR)) (1).torrent', remove_content=True)
    'The.Band.-.Let.Me.Out.-.1993.torrent'

    >>> remove_braces('Able Baker [1981].mkv', remove_content=False)
    'Able.Baker.1981.mkv'

    >>> remove_braces('Able Baker [1981].mkv', remove_content=True)
    'Able.Baker.mkv'

    >>> remove_braces('[able].baker.charlie.S2...01.[720p.H264][AAAAAAAA].mkv')
    'baker.charlie.S2.01.[AAAAAAAA].mkv'
    """
    brace_stack = Stack()
    content_stack = Stack()
    output = ''
    for i, c in enumerate(filename):
        #print c, output, content_stack.content
        # looking for an openbracket
        if c in braces:
            brace_stack.push(braces[c])
            content_stack.push('')
        elif brace_stack:
            # looking for a closebracket
            if c == brace_stack.peek():
                brace_stack.pop()
                # contains brace content
                if is_checksum(content_stack.peek()):
                    if preserve_checksum:
                        # append the checksum to the output
                        content_stack.push('[' + content_stack.pop().upper() + ']')
                    else:
                        content_stack.pop()
                else:
                    # other content inside brackets
                    if remove_content:
                        content_stack.pop()
                        # remove the content
                    else:
                        content_stack.push('')
            else:
                content_stack.replace_first(content_stack.peek() + c)
        else:
            # new character, and we're free of brackets
            if content_stack:
                while content_stack:
                    output = dotjoin(output, content_stack.lastitem())
                output = output + '.'
            output += c

    output = endot(output)
    return output

class Stack:
    """
    A stack, with some extra functions for matching-brackets without reversing
    """
    content = []

    def __nonzero__(self):
        return bool(self.content)

    def push(self, item):
        self.content = [item] + self.content

    def pop(self):
        item = self.content[0]
        self.content = self.content[1:]
        return item

    def peek(self):
        if self.content:
            return self.content[0]
        else:
            return ''

    def append(self, item):
        self.content.append(item)

    def replace_first(self, item):
        if self.content:
            self.content[0] = item
        else:
            self.content = [item]

    def lastitem(self):
        item = self.content[-1]
        self.content = self.content[:-1]
        return item


if __name__ == '__main__':
    import doctest
    doctest.testmod()

