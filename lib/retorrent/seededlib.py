""" retorrent.seededlib """

import os

from os.path import abspath, expanduser, isdir, realpath
from os.path import join as pjoin

default_seeddir = expanduser('~/seed')


def is_seeded(args, seeddir=default_seeddir):
    seed_map = [(root, dirs, files) for root, dirs, files in os.walk(seeddir, followlinks=True)]

    seed_filepaths = {}

    for root, _, files in seed_map:
        # build a flat list of the defeferenced symlinks.
        seed_filepaths[realpath(root)] = abspath(root)
        seed_filepaths.update({realpath(pjoin(root, file_)): pjoin(root, file_) for file_ in files})

    seeded = {}
    unseeded = []
    for arg in args:
        res = is_seeded_singleitem(arg, seed_filepaths)
        if res:
            seeded[arg] = res
        else:
            unseeded.append(arg)

    return seeded, unseeded


# Passed a file -> Somewhere in seed is a symlink to that file
# Passed a dir ->     1./ Somewhere in seed is a symlink to that dir
#                    2./ Somewhere in seed is a symlink to the dir's contents
def is_seeded_singleitem(path, seed_filepaths):
    the_path = realpath(path)

    for derefd_symlink, symlink in list(seed_filepaths.items()):
        if the_path == derefd_symlink:
            return symlink

    # let's now look at dir contents
    if isdir(the_path):
        for each_dir in os.listdir(the_path):
            res = is_seeded_singleitem(pjoin(the_path, each_dir), seed_filepaths)
            if res:
                return res
    return None
