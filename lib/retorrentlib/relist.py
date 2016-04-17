"""
retorrent.relist

A set of utility functions for dealing with lists in a retorrent-specific manner,
usually dealing with tokenised filenames
"""
from redecorators import tracelogdecorator

from .braced import is_checksum


@tracelogdecorator
def lowercase_non_checksums(filename_split):
    return [item.lower() if not is_checksum(item) else item for item in filename_split]


def _replace_items(split_fn, index, new_string, num_items=2):
    return split_fn[0:index] + [new_string] + split_fn[index + num_items:]


@tracelogdecorator
def replace_singleitem(split_fn, index, new_string):
    return _replace_items(split_fn, index, new_string, num_items=1)


@tracelogdecorator
def replace_doubleitem(split_fn, index, new_string):
    return _replace_items(split_fn, index, new_string, num_items=2)
