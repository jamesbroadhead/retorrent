#!/usr/bin/env python

from os import listdir
from os.path import abspath, basename, expanduser
from os.path import join as pjoin

from torrentparse.torrentparse import TorrentParser as TP

def gen_map():
    tfiledir = abspath(expanduser('~/torrents/torrentfiles'))
    tfiles = [ pjoin(tfiledir, f)
               for f in listdir(tfiledir)
               if f.endswith('torrent')]

    files_tfiles = {}
    for tfile in tfiles:
        files_details = TP(tfile).get_files_details()
        for filename, size in files_details:
            files_tfiles[filename] = tfile
    return files_tfiles

def tfile_from_filename(filename, files_tfiles=None):
    if files_tfiles is None:
        files_tfiles = gen_map()

    filename = basename(filename)
    return files_tfiles.get(filename, '')
