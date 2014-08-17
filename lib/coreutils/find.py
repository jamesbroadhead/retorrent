#!/usr/bin/env python

import os
from os.path import isfile, islink
import fnmatch


def find(top_dir, pattern=None, filters=None):
    """
    Based on:
    http://www.dabeaz.com/generators-uk/genfind.py

    @param pattern: an fnmatch pattern. If unset or None, '*'
    @param filters: a list of functions to filter result paths through
    """
    if pattern is None:
        pattern = '*'
    if filters is None:
        filters = []

    for path, dirlist, filelist in os.walk(top_dir):
        for name in fnmatch.filter(filelist, pattern):
            full_path = os.path.join(path,name)
            if all([f(full_path) for f in filters]):
                yield full_path

def find_broken_symlinks(top_dir):
    filters = [
        lambda f: not isfile(f),
        islink
    ]
    return find(top_dir, pattern=None, filters=filters)
