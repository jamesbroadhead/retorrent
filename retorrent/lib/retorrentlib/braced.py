#!/usr/bin/python
"""
Utility module for functions dealing with strings containing substrings inside braces

"""
import datetime

from redecorators.memoize import memoize_record_interactive
from redecorators.tracelogdecorator import tracelogdecorator
from retorrentlib.optionator import booloptionator
from retorrentlib.restring import dotjoin, endot

braces = {
    '[' : ']',
    '{' : '}',
    '(' : ')'
}
hexdigits = '0123456789abcdefABCDEF' + u'0123456789abcdefABCDEF'

@tracelogdecorator
def is_checksum(item):
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

    """
    for segment in filename.split('.'):

        if is_checksum(segment):
            if len(segment) == 8:
                segment = '[%s]' % (segment)
            return segment.upper()
    return ''

@tracelogdecorator
def remove_braces(filename, preserve_checksum=True):
    """
    Removes braces and internal content, with special rules for checksums and years

    Optionally preserves content, removing braces

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
                peeked_content = content_stack.peek()
                if is_checksum(peeked_content):
                    if preserve_checksum:
                        # append the checksum to the output
                        content_stack.push('[' + content_stack.pop().upper() + ']')
                    else:
                        content_stack.pop()

                elif is_year(peeked_content):
                    # preserve the year sans-brackets
                    content_stack.push(content_stack.pop())

                else:
                    # remove the content
                    content_stack.pop()

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

def ask_is_year(item):
    if booloptionator('Does ' + item + ' represent a year?'):
        return True
    return False

@memoize_record_interactive
def is_year(item, interactive=True):
    thisyear = datetime.datetime.now().year
    if item.isdigit() and len(item) == 4 and int(item) <= thisyear:
        if not interactive:
            return False
        return ask_is_year(item)

    return False

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
