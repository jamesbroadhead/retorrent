#!/usr/bin/env python
"""
Usage:
    rm_seeded TARGETS...
    rm_seeded [ -s | --skip-targets ] TARGETS...

Options:
    -s --skip-targets    Delete everything except the file passed

#Future: this leaves junk dirs in `seeddir`, which may be empty, or contain .nfos or similar which have been ignored by retorrent.
    #1: Travel up paths inside `seeddir` & rm if empty
    #2: use the same filtering logic from retorrent & rm if nothing else remains
"""
import os
from os.path import abspath, realpath
import sys

from docopt import docopt

from .. import seededlib
from ..confparse import parse_retorrentconf
from ..find_tfile import gen_map, tfile_from_filename
from ..remreffer import remref


# pylint: disable=too-many-locals
def _main(targets, skip_targets=False):
    config, _ = parse_retorrentconf()
    seeddir = config['seeddir']
    seed_tfilesdir = config['seedtorrentfilesdir']

    # the list passed. Generally, symlinks in ~/video
    remove_targets = []
    for t in targets:
        if os.path.exists(t):
            remove_targets.append(abspath(t))
        else:
            print("Couldn't find %r" % (t,))

    if not remove_targets:
        print('No extant targets!')
        sys.exit(1)

    seeded, unseeded = seededlib.is_seeded(remove_targets, seeddir=seeddir)

    files_tfiles = gen_map(seed_tfilesdir)
    #pylint: disable=unused-variable
    tfiles = [
        tfile_from_filename(
            seedpath, seed_tfilesdir, files_tfiles=files_tfiles)
        for videopath, seedpath in list(seeded.items())
    ]

    # unseeded: list of args which are not seeded
    # tfiles: list of tfiles
    # seeded.values() : list of symlinks in ~/seed
    # seeded.keys() : list of abspath'd arguments to this (~/video/*)
    # *We are not passing realpath'd arguments* -- remref will do that
    to_delete = unseeded + tfiles + list(seeded.keys()) + list(seeded.values())

    to_skip = []
    if skip_targets:
        to_skip = [realpath(abspath(rt)) for rt in remove_targets]

    res = remref(to_delete, to_skip=to_skip)

    print('Remember: if there were dirs in seed/, they will remain!')

    return res


def main():
    arguments = docopt(__doc__)
    sys.exit(_main(arguments['TARGETS'], skip_targets=arguments['--skip-targets']))


if __name__ == '__main__':
    main()
