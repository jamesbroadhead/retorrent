#!/usr/bin/env python
"""
Create symlinks, joining together retorrent content dirs

Usage:
    symlinker
    symlinker [-s | --smbsafe]

Arguments:
    -s --smbsafe      Create symlinks in the smbsafe directory with Samba-safe paths
"""

import os
from os.path import abspath, basename, dirname, expanduser, isdir, isfile, lexists
from os.path import islink, realpath
from os.path import exists as pexists
from os.path import join as pjoin

from docopt import docopt

from os_utils.os_utils import mkdir_p, smbify, sym_sametarget
from .. import confparse

debug = False


def debugprint(string, debuglevel=1):
    """
    debuglevel = 0 - always print
    debuglevel = 1 - print if -d
    debuglevel = 2 - print if -dd
    """
    if debuglevel <= debug:
        print string


# there sure are!
#pylint: disable=too-many-branches,too-many-locals,too-many-statements
def _main(smbsafe=False):
    _, categories_conf = confparse.parse_retorrentconf()

    for_postprocessing = {}
    for _, category in categories_conf.items():
        # print category
        category_home = category['symlink_path']
        if smbsafe:
            category_home = category['smbsafe_symlink_path']

        mkdir_p(expanduser(category_home))
        debugprint('Considering: %s' % (basename(category_home)))

        removed = []
        # remove broken symlinks
        for elem in os.listdir(category_home):
            elem_path = pjoin(category_home, elem)

            if not islink(elem_path):

                if isfile(elem_path):
                    print '!! file in symlink dir: %s' % (elem_path)
                elif not len(os.listdir(elem_path)):
                    os.rmdir(elem_path)
                else:
                    for f in os.listdir(elem_path):
                        fpath = pjoin(elem_path, f)
                        if not islink(fpath):
                            print 'Non-symlinked file detected in folder %s in %s' % (
                                basename(fpath), elem_path)
                            print '\t Non-symlinked folders should only contain symlinks'
                        elif not isfile(fpath):
                            # broken symlink
                            os.remove(fpath)

            else:
                if lexists(elem_path) and not pexists(elem_path):
                    print 'Broken symlink! Removing.', elem
                    removed += [elem]
                    os.remove(elem_path)

        if category_home in category['content_paths']:
            print 'The content home is in the list of content paths. Cannot continue.'
            continue

        # /mnt/foo/video/tv, /mnt/bar/video/tv etc.
        for content_dir in category['content_paths']:
            debugprint('Looking at: %r' % (content_dir,))
            if not pexists(content_dir):
                # dir doesn't exist, no need to create it & check it
                continue

            for content in os.listdir(content_dir):
                content = content.decode('utf-8')
                content_path = pjoin(content_dir, content)
                debugprint('Examining: %s' % (content_path,), 2)

                # empty dir in content dir
                if isdir(content_path) and not len(os.listdir(content_path)):
                    os.rmdir(content_path)
                    print '%s: removed empty content dir' % (content_path,)
                    continue

                # symlinks in content dir
                elif islink(content_path):
                    print '%s: symlink in content dir'
                    if not pexists(content_path):
                        print '%s: symlink was broken, removing'
                        os.remove(content_path)

                # content can either be movie.avi or series.name/
                content_abspath = abspath(pjoin(content_dir, content))

                symlink_path = abspath(pjoin(category_home, content))
                if smbsafe:
                    symlink_path = abspath(pjoin(category_home, smbify(content)))

                # missing or broken symlink
                if not pexists(symlink_path):
                    if islink(symlink_path):
                        os.remove(symlink_path)

                    os.symlink(content_abspath, symlink_path)
                    if content in removed:
                        print 'Replaced a broken symlink', content

                # symlink with same name already exists
                #     and doesn't point to same location
                elif islink(symlink_path) and \
                    not realpath(symlink_path) == \
                        realpath(content_abspath):

                    debugprint('%s already exists, and there are two candidates, %s and %s' %
                               (symlink_path, realpath(symlink_path), realpath(content_abspath)))
                    oldlink_realpath = realpath(symlink_path)

                    # they're both links to different directories
                    #    create dir, populate with symlinks to the content
                    #    in both
                    if isdir(oldlink_realpath) and \
                            isdir(content_abspath):
                        # remove oldlink
                        os.remove(symlink_path)
                        # mkdir foo
                        mkdir_p(symlink_path)

                        link_contents(oldlink_realpath, symlink_path)
                        link_contents(content_abspath, symlink_path)
                    else:
                        print 'Duplicate files, can\'t combine :('
                        print '\t', oldlink_realpath
                        print '\t', content_abspath

                # dir found in category_home.
                #    Broken symlinks and empty dirs should be gone already
                elif not islink(symlink_path) and \
                        isdir(symlink_path):
                    debugprint('Will post-process: %s' % (symlink_path,))
                    for_postprocessing.setdefault(symlink_path, []).append(content_abspath)
                else:
                    # the symlink exists + points at this content :D
                    debugprint('%s - OK' % (symlink_path,), 2)

    for symlink_path, content_paths in for_postprocessing.iteritems():
        debugprint('Postprocessing: %s' % (symlink_path,))
        for c in content_paths:
            link_contents(c, symlink_path)

    # prune dirs full of symlinks to the same place
    for elem in os.listdir(category_home):

        if isdir(elem):
            #If dir is full of symlinks, and all symlinks are to the same dir,
            #    remove all symlinks, then symlink the dir
            symlinkdir_contents_paths = [pjoin(symlink_path, l) for l in os.listdir(symlink_path)]

            if (all([islink(f) for f in symlinkdir_contents_paths]) and
                    all_symlinks_to_same_dir(content_abspath, symlinkdir_contents_paths)):

                for f in symlinkdir_contents_paths:
                    if islink(f):
                        os.remove(f)
                    else:
                        print 'ERROR! Tried to remove a file! %s' % (f)
                os.rmdir(symlink_path)
                print '\t%s no longer sourced from multiple locations' % (symlink_path,)
                os.symlink(content_abspath, symlink_path)
            else:
                link_contents(content_abspath, symlink_path)
                print '\t%s: sourced from multiple locations' % (symlink_path,)


def link_contents(content_path, linkdir_path):
    content_realpath = realpath(content_path)
    for fn in os.listdir(content_realpath):
        f_realpath = pjoin(content_realpath, fn)
        f_sympath = pjoin(linkdir_path, fn)

        if not pexists(f_sympath):
            os.symlink(f_realpath, f_sympath)
        elif pexists(f_sympath) and not sym_sametarget(f_sympath, f_realpath):
            print 'Duplicate content found for %s in:' % (f_sympath,)
            print '==>', realpath(f_sympath)
            print '   ', realpath(f_realpath)
        else:
            # symlink exists, but points to same location.
            pass


def all_symlinks_to_same_dir(d, symlinks):
    print d
    for s in symlinks:
        if not abspath(dirname(realpath(s))) == abspath(d):
            return False
    return True


def main():
    arguments = docopt(__doc__)
    _main(smbsafe=arguments['--smbsafe'])


if __name__ == '__main__':
    main()
