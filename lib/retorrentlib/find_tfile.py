#!/usr/bin/env python

from os.path import basename, expanduser, isdir, isfile
from os.path import join as pjoin

from os_utils.os_utils import listdir
from torrentparse.torrentparse import TorrentParser as TP

debug = True

def find_tfiles(paths, tfilesdir):
    tfilesdir = expanduser(tfilesdir)
    files_tfiles = gen_map(tfilesdir)

    return [ tfile_from_filename(path, tfilesdir, files_tfiles)
             for path in paths ]

def tfile_details(tfile_path):
    files_tfile = {}
    try:
        files_sizes = {
            k.decode('utf-8'): v
            for k, v in TP(tfile_path).get_files_details()}

        for filename, size in files_sizes.items():
            files_tfile[filename] = tfile_path
    except Exception:
        pass
    return files_tfile

def gen_map(tfilesdir):
    tfiles = [ pjoin(tfilesdir, f)
               for f in listdir(tfilesdir)
               if f.endswith('torrent')]

    files_tfiles = {}
    for tfile in tfiles:
        files_tfiles.update(tfile_details(tfile))
    return files_tfiles

def tfile_from_filename(filename, tfilesdir, files_tfiles=None):
    """
    @param: files_tfiles : pre-generated output from gen_map
    """
    if files_tfiles is None:
        files_tfiles = gen_map(tfilesdir)

    if isdir(filename):
        # cheat, and get a file inside the dir
        filename = pick_file(filename)

    filename = basename(filename)
    return files_tfiles.get(filename, '')

def pick_file(dirpath):
    dircontent = listdir(dirpath)

    for f in dircontent:
        path = pjoin(dirpath, f)
        if isfile(path):
            return f
    raise Exception('Passed a dir with no content!')
