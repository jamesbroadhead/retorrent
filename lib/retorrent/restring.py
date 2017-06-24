#!/usr/bin/python
"""
retorrent.restring

A set of utility functions for dealing with strings in a retorrent-specific manner,
usually dealing with paths
"""
from redecorators import tracelogdecorator
from os_utils.os_utils import str2utf8

alphabet = "abcdefghijklmnopqrstuvwxyz"
eng_numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


###
# Functions dealing with split filenames and .'s
###
@tracelogdecorator
def dotjoin(*args):
    stripped = [a.strip('. ') for a in args if a]
    return '.'.join(stripped)


endottables = [' ', '_']


@tracelogdecorator
def endot(string):
    for e in endottables:
        string = string.replace(e, '.')
    while '..' in string:
        string = string.replace('..', '.')
    string = string.strip('.')
    return string


###
# Other functions
###
@tracelogdecorator
def remove_camelcase(filename):
    """
    Despite the name, remove internal camelCase only.
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


@tracelogdecorator
def remove_zwsp(filename):
    """
    removes Zero Width Spaces from a string.
    Returns in UTF-8. HERE BE DRAGONS
    """
    zwsp = '\u200b'

    ufilename = str2utf8(filename)

    while zwsp in ufilename:
        ufilename.replace(zwsp, '')
    return ufilename


##
# the alphabet
##
def conv_from_alphabet(letter):
    """ eg. 'a' => '1' """
    ordinal = alphabet.index(letter) + 1
    return str(ordinal)


##
# english-language numbers
##
def conv_eng_number(somestring):
    """ eg. "one" => '1' """
    ordinal = eng_numbers.index(somestring) + 1
    return str(ordinal)
