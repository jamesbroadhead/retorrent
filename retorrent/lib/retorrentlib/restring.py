#!/usr/bin/python
"""
retorrent.restring

A set of utility functions for dealing with strings in a retorrent-specific manner,
usually dealing with paths)
"""

###
# Functions dealing with split filenames and .'s
###
def add_necc_dots(filename):
    """
    deprecated. use endot instead
    """
    divide_items = ["["]
    for item in divide_items:
        if item in filename:
            index = filename.find(item)
            while not index == -1:
                if not index == 0 and not filename[index-1] == ".":
                    filename = filename[0:index] + "." + filename[index:]
                # index + 2 is the next char after the item
                index = filename[index+2:].find(item)

    return filename

def dotjoin(*args):
    stripped = [ a.strip('. ') for a in args if a]
    return '.'.join(stripped)

def endot(string):
    string = string.replace(' ', '.')
    string = string.replace('_', '.')
    while '..' in string:
        string = string.replace('..', '.')
    return string

def remove_dupe_dots(filename):
    """
    deprecated. use endot instead
    """
    filename = filename.strip('.')

    ddot_index = filename.find("..")
    while not ddot_index == -1:
        filename = filename[0:ddot_index] + filename[ddot_index+1:]
        ddot_index = filename.find("..")

    return filename

###
# Other functions
###

def remove_camelcase(filename):
    """
    Despite the name, remove internal camelCase only.

    >>> remove_camelcase('')
    ''

    >>> remove_camelcase('foo')
    'foo'

    >>> remove_camelcase('fooBar')
    'foo.bar'
    """
    if not filename:
        return filename

    outfilename = filename[0]
    for prev, curr in zip(filename[0:-1], filename[1:]):
        if prev.islower() and curr.isupper():
            outfilename += "."
            curr = curr.lower()
        outfilename += curr
    return outfilename

if __name__ == '__main__':
    import doctest
    doctest.testmod()

def remove_zwsp(filename):
    """
    # removes Zero Width Spaces from a string.
    # Returns in UTF-8. HERE BE DRAGONS
    """
    zwsp = u'\u200b'

    ufilename = filename
    if not type(ufilename) == type(u'unicode'):
        ufilename = unicode(filename,'utf-8', errors='ignore')

    while zwsp in ufilename:
    #    ufilename = ufilename[0:ufilename.find(zwsp)] + ufilename[ufilename.find(zwsp)+len(zwsp):]
        ufilename.replace(zwsp, '')
    return ufilename
