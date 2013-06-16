#!/usr/bin/python

import os

import confparse

def read_from_file():
    filepath = confparse.find_removelist()

    stripsymbols = ' \n'

    # don't catch - retorrent can't function without a removeset
    with open(filepath) as f:
        rmlist = set([ elem.strip(stripsymbols) for elem in f.readlines() ])

    return rmlist

def write_to_file(removeset):
    filepath = confparse.find_removelist()

    rmlist_out = [ i+'\n' for i in removeset ]
    rmlist_out.sort()

    with open(filepath,'w') as f:
        f.writelines(rmlist_out)
        os.fsync(f)

def add_and_sync(removeset, item):
    removeset.add(item)

    write_to_file(removeset)
    return removeset
