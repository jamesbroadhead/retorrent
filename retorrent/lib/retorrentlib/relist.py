"""
retorrent.relist

A set of utility functions for dealing with lists in a retorrent-specific manner,
usually dealing with tokenised filenames
"""

def remove_elements_based_on_list(filename_split, remove_set):
    """
    Remove items from the filename_split if they exist in the remove_set.
    Preserve the final element regardless.

    >>> remove_elements_based_on_list(['foo', 'bar', 'baz'], ['bar'])
    ['foo', 'baz']

    >>> remove_elements_based_on_list(['foo', 'bar', 'baz'], ['baz'])
    ['foo', 'bar', 'baz']

    >>> remove_elements_based_on_list(['foo', 'bar', 'baz'], ['baz', 'foo', 'bar'])
    ['baz']
    """

    output = [ item for item in filename_split[0:-1] if not item in remove_set ]
    output.append(filename_split[-1])
    return output


if __name__ == '__main__':
    import doctest
    doctest.testmod()

