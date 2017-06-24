#!/usr/bin/python
"""
Utility module for functions dealing with strings containing substrings inside braces

"""
from datetime import datetime

from redecorators import memoize_record_interactive, tracelogdecorator

from .optionator import booloptionator
from .restring import dotjoin, endot

braces = {'[': ']', '{': '}', '(': ')'}
hexdigits = '0123456789abcdefABCDEF' + '0123456789abcdefABCDEF'


@tracelogdecorator
def is_checksum(item):
    # 8-digit checksum + braces
    if len(item) == 10:
        if not item[0] in braces or not item[-1] == braces.get(item[0], None):
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
def remove_braces(filename, preserve_checksum=True, interactive=False):
    """
    Removes braces and internal content, with special rules for checksums and years

    Optionally preserves content, removing braces

    """
    #pylint: disable=too-many-branches
    brace_stack = Stack()
    content_stack = Stack()
    output = ''
    for c in filename:
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

                elif is_year(peeked_content, interactive=interactive):
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


@tracelogdecorator
@memoize_record_interactive
def is_year(item, interactive=True):
    """
    Assumes that two-digit years are in the 19xx's... millenium bug.
    """
    thisyear = datetime.now().year

    if len(item) == 2:
        # two digit years belong in the 19xx's ...?
        item = '19%s' % (item,)

    if item.isdigit() and len(item) == 4 and int(item) <= thisyear:
        if not interactive:
            # let's take 1940+ as a year.
            if 1940 <= int(item) <= thisyear:
                return True
            return False
        return booloptionator('Does ' + item + ' represent a year?')
    return False


class Stack(object):
    """
    A stack, with some extra functions for matching-brackets without reversing
    """
    content = []

    def __init__(self):
        pass

    def __bool__(self):
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
