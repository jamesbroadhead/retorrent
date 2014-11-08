"""
retorrent.relist

A set of utility functions for dealing with lists in a retorrent-specific manner,
usually dealing with tokenised filenames
"""

from retorrentlib.braced import is_checksum

def remove_nonfinal_elements_if_in_set(filename_split, remove_set):
    """
    Remove items from the filename_split if they exist in the remove_set.
    Preserve the final element regardless.

    >>> remove_nonfinal_elements_if_in_set(['foo', 'bar', 'baz'], set(['bar']))
    ['foo', 'baz']

    >>> remove_nonfinal_elements_if_in_set(['foo', 'bar', 'baz'], set(['baz']))
    ['foo', 'bar', 'baz']

    >>> remove_nonfinal_elements_if_in_set(['foo', 'bar', 'baz'], set(['baz', 'foo', 'bar']))
    ['baz']
    """
    output = [item for item in filename_split[0:-1] if not item in remove_set]
    output.append(filename_split[-1])
    return output


def lowercase_non_checksums(filename_split):
    """
    >>> lowercase_non_checksums(['foo', 'bar', 'baz'])
    ['foo', 'bar', 'baz']

    >>> lowercase_non_checksums(['FOO', 'BAR', 'BAZ'])
    ['foo', 'bar', 'baz']

    >>> lowercase_non_checksums(['foo', 'BAR', 'baz'])
    ['foo', 'bar', 'baz']

    >>> lowercase_non_checksums(['foo', 'AAAAAAAA', 'baz'])
    ['foo', 'AAAAAAAA', 'baz']

    >>> lowercase_non_checksums(['foo', '[AAAAAAAA]', 'baz'])
    ['foo', '[AAAAAAAA]', 'baz']
    """

    return [item.lower()
            if not is_checksum(item) else item
            for item in filename_split]


if __name__ == '__main__':
    import doctest
    doctest.testmod()

