""" retorrent.removeset """

import os

from . import confparse


def read_from_file(path):
    with open(path) as fh:
        return {elem.strip(' \n') for elem in fh.readlines() if elem.strip(' \n')}


def write_to_file(removeset):
    path = confparse.find_removelist()
    return _write_to_file(path, removeset)


def _write_to_file(path, removeset):

    rmlist_out = [i + '\n' for i in removeset if i]
    rmlist_out.sort()

    with open(path, 'w') as f:
        f.writelines(rmlist_out)
        os.fsync(f)


def add_and_sync(removeset, item):
    removeset.add(item)

    write_to_file(removeset)
    return removeset
