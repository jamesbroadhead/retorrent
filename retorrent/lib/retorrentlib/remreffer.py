import os
from subprocess import Popen

def remref(args):
    paths = trim_trailing_slashes(args)

    print "Would delete:"
    pathlist = []
    for item in paths:
        pathlist.extend(add_item(item))

    pathlist = uniq(pathlist)

    for item in pathlist:
        print item

    command = ['rm','-Irv']
    command.extend(pathlist)

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
            pathlist.extend(add_item(os.path.join(item,subitem)))

    pathlist.reverse()

    return pathlist

def trim_trailing_slashes(args):
    return [ arg[0:-1] if arg[-1] == '/' else arg for arg in args  ]

def uniq(pathlist):
    """ preserving sort order, remove duplicates """
    out = []
    for p in pathlist:
        if not p in out:
            out.append(p)
    return out
