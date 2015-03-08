"""
retorrent.relist

A set of utility functions for dealing with lists in a retorrent-specific manner,
usually dealing with tokenised filenames
"""
from redecorators import tracelogdecorator

from .braced import is_checksum

@tracelogdecorator
def lowercase_non_checksums(filename_split):
    return [item.lower()
            if not is_checksum(item) else item
            for item in filename_split]

@tracelogdecorator
def replace_doubleitem(split_fn, index, new_string):
    return split_fn[0:index] + [new_string] + split_fn[index+2:]


