"""" retorrentlib.remreffer """

import os
from subprocess import Popen


def remref(to_delete, to_skip=None):
    if to_skip is None:
        to_skip = []
    to_skip = set(to_skip)

    paths = trim_trailing_slashes(to_delete)

    pathlist = []
    for item in paths:
        pathlist.extend(add_item(item))

    skipping = set([p for p in pathlist if p in to_skip])
    deleting = [p for p in pathlist if not p in skipping]

    if skipping:
        print 'Skipping:'
        for s in skipping:
            print s

    if not deleting:
        print 'Nothing to delete'
        return 0

    print "Would delete:"
    for p in deleting:
        print p

    return do_delete(deleting)


def do_delete(deleting):
    command = ['rm', '-Irv']
    command.extend(deleting)

    p = Popen(command)
    sts = os.waitpid(p.pid, 0)[1]
    return sts


def add_item(item):
    pathlist = []

    # add the item. if it's a symlink, add the symlink
    if os.path.exists(item):
        pathlist.append(os.path.abspath(item))

    if os.path.islink(item):
        # add the real item
        if os.path.exists(os.path.realpath(item)):
            pathlist.append(os.path.abspath(os.path.realpath(item)))

    # isdir(symlink) == True
    if os.path.isdir(item):
        for subitem in os.listdir(item):
            pathlist.extend(add_item(os.path.join(item, subitem)))

    pathlist.reverse()

    return pathlist


def trim_trailing_slashes(args):
    return [arg[0:-1] if arg[-1] == '/' else arg for arg in args]


def uniq(pathlist):
    """ preserving sort order, remove duplicates """
    out = []
    for p in pathlist:
        if not p in out:
            out.append(p)
    return out
