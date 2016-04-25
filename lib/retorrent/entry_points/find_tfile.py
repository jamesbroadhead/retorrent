#!/usr/bin/env python
"""
Usage:
    find_tfile TARGETS...
    find_tfile --tfilesdir=DIR TARGETS...

Options:
    -t, --tfilesdir The .torrent dir to search within
"""
from os.path import abspath, expanduser
import sys

from docopt import docopt

from retorrent.find_tfile import find_tfiles


def _get_results(targets, tfilesdir):
    tfilesdir = expanduser(tfilesdir)
    return [i for i in find_tfiles(targets, tfilesdir) if i is not None]


def _main(targets, tfilesdir, out=sys.stdout):
    results = _get_results(targets, tfilesdir)

    output = ' '.join(results)
    out.writelines([output])


def main():
    arguments = docopt(__doc__)
    default_tfilesdir = abspath(expanduser('~/torrents/torrentfiles'))

    targets_ = arguments['TARGETS']
    tfilesdir_ = arguments['--tfilesdir'] or default_tfilesdir

    _main(targets_, tfilesdir_)


if __name__ == '__main__':
    main()
