"""
retorrent.relist

A set of utility functions for dealing with lists in a retorrent-specific manner,
usually dealing with tokenised filenames
"""

from .braced import is_checksum

def lowercase_non_checksums(filename_split):
    return [item.lower()
            if not is_checksum(item) else item
            for item in filename_split]
