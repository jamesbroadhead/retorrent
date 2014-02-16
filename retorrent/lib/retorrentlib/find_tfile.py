#!/usr/bin/env python

from os import listdir
from os.path import abspath, basename, expanduser
from os.path import join as pjoin

from torrentparse.torrentparse import TorrentParser as TP

default_path = abspath(expanduser('~/torrents/torrentfiles'))

def gen_map(tfilesdir=default_path):
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

def tfile_from_filename(filename, files_tfiles=None, tfilesdir=default_path):
    """
    @param: files_tfiles : pre-generated output from gen_map
    """
    if files_tfiles is None:
        files_tfiles = gen_map(tfilesdir)

    filename = basename(filename)
    return files_tfiles.get(filename, '')
