#!/usr/bin/env python3
"""
A utility to clean a seed directory when symlinks inside it are broken.
Attempts to replace broken symlinks with those pointing to a content_root_path
if a file with the same source name as the broken symlink exists
"""
from retorrent.confparse import parse_retorrentconf
from retorrent.find_tfile import gen_map, tfile_from_filename
from jboutils.find import find

import os
from os.path import islink, realpath
from os.path import exists as pexists
from os.path import join as pjoin
import sys


def psplit(path):
    """ os.path.split doesn't do what you'd expect """
    path = os.path.normpath(path)
    return path.split(os.sep)


def is_broken_symlink(path):
    return islink(path) and not pexists(path)


def delete_old_seed_entry(path_to_symlink, seeddir, files_tfiles):
    # find matching torrentfile - but it may already not exist
    # delete symlink
    tfile = tfile_from_filename(path_to_symlink, seeddir, files_tfiles)
    if tfile:
        # TODO: this doesn't work
        print('deleting "{}"'.format(tfile))
        os.remove(tfile)
    print('deleting "{}"'.format(path_to_symlink))

    try:
        os.remove(path_to_symlink)
    except FileNotFoundError:  # Bugfix: don't know why this is happening, but the end result is good so I don't care
        print('{} was already deleted...'.format(path_to_symlink))


def _calculate_content_root_path(path_to_symlink, path_to_content, crp, symlink_path, seeddir,
                                 files_tfiles):
    split_path = psplit(path_to_content)

    for i in range(len(split_path)):
        trial_path = pjoin(symlink_path, *split_path[i:])
        if pexists(trial_path):
            return pjoin('/', *split_path[0:i])

    print('Failed to find a content_root_path from {}'.format(path_to_content))


def _relink(path_to_symlink, path_to_content, crp, symlink_path, seeddir, files_tfiles):
    new_symlink_target = path_to_content.replace(crp, symlink_path)
    if not pexists(new_symlink_target):
        print('Failed to find content for {}'.format(new_symlink_target))
        delete_old_seed_entry(path_to_symlink, seeddir, files_tfiles)
    else:
        print('relinking: "{}" to "{}"'.format(path_to_symlink, new_symlink_target))
        os.remove(path_to_symlink)
        os.symlink(new_symlink_target, path_to_symlink)


def relink(path_to_symlink, content_root_paths, symlink_path, seeddir, files_tfiles):
    path_to_content = realpath(path_to_symlink)
    files_tfiles = None

    for crp in content_root_paths:
        if path_to_content.startswith(crp):
            _relink(path_to_symlink, path_to_content, crp, symlink_path, seeddir, files_tfiles)

    # the symlink in seed has a content_root_path which is no longer in the retorrent
    # config eg. a failed disk
    crp = _calculate_content_root_path(path_to_symlink, path_to_content, crp, symlink_path, seeddir,
                                       files_tfiles)
    if crp is not None:
        _relink(path_to_symlink, path_to_content, crp, symlink_path, seeddir, files_tfiles)
    else:
        # The content almost certainly doesn't exist

        # 2020-06: added this to the 'else' block, where it seems to belong
        delete_old_seed_entry(path_to_symlink, seeddir, files_tfiles)


def _main():
    conf, _ = parse_retorrentconf()

    content_root_paths = conf['content_root_paths']
    seeddir = conf['seeddir']
    symlink_path = conf['symlink_path']
    files_tfiles = gen_map(seeddir)

    for filepath in find(seeddir):
        if is_broken_symlink(filepath):
            relink(filepath, content_root_paths, symlink_path, seeddir, files_tfiles)


def main():
    print('This script has bugs!')
    print('It seems to do "relinking", then it deletes the symlink it just made!')
    print('Script was edited in 2020-06 which may have fixed it, but please run with care...')
    _main()


if __name__ == '__main__':
    main()
