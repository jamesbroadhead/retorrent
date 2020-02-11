#!/usr/bin/env python
"""
unseed_broken: Incomplete tool for post-deletion cleanup of seeddir

Usage:
    unseed_broken
    unseed_broken FILEDIR
"""
from os.path import abspath, expanduser, isdir
from os.path import join as pjoin
import sys

from docopt import docopt

from jboutils.find import find_broken_symlinks
from ..find_tfile import find_tfiles


def _main(filedir):
    tfilesdir = pjoin(filedir, 'torrentfiles')
    if not isdir(filedir) or not isdir(tfilesdir):
        print('dir missing!')
        sys.exit(1)

    broken_symlinks_gen = find_broken_symlinks(filedir)
    tfiles_for_broken_symlinks = set(find_tfiles([sym for sym in broken_symlinks_gen], tfilesdir))
    # arguably, look up other symlinks which belong to this tfile as well

    return do_deletions(tfiles_for_broken_symlinks)


def do_deletions(tfiles_for_broken_symlinks):
    """
    TODO.
    ask,
    delete files,
    delete tfiles,
    try to rmdir the dir that the files were in (if != filedir)
    """
    return tfiles_for_broken_symlinks


def main():
    arguments = docopt(__doc__)
    default_filedir = abspath(expanduser('~/seed'))

    _main(arguments['--filedir'] or default_filedir)


if __name__ == '__main__':
    main()
