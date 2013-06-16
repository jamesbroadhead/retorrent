#!/usr/bin/python
"""
retorrent.restring

A set of utility functions for dealing with strings in a retorrent-specific manner,
usually dealing with paths
"""

###
# Functions dealing with split filenames and .'s
###
def dotjoin(*args):
    stripped = [ a.strip('. ') for a in args if a]
    return '.'.join(stripped)

def endot(string):
    string = string.replace(' ', '.')
    string = string.replace('_', '.')
    while '..' in string:
        string = string.replace('..', '.')
    return string

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



if __name__ == '__main__':
    import doctest
    doctest.testmod()


