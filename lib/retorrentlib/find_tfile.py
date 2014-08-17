#!/usr/bin/env python

from os import listdir
from os.path import basename, expanduser, isdir, isfile
from os.path import join as pjoin

from torrentparse.torrentparse import TorrentParser as TP


def find_tfiles(paths, tfilesdir):
    tfilesdir = expanduser(tfilesdir)
    files_tfiles = gen_map(tfilesdir)

    return [ tfile_from_filename(path, tfilesdir, files_tfiles)
             for path in paths ]


def gen_map(tfilesdir):
    tfiles = [ pjoin(tfilesdir, f)
               for f in listdir(tfilesdir)
               if f.endswith('torrent')]

    files_tfiles = {}
    for tfile in tfiles:
        try:
            files_details = TP(tfile).get_files_details()
            for filename, size in files_details:
                files_tfiles[filename] = tfile
        except:
            pass
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
