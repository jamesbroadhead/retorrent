""" retorrent.find_tfile """

from os.path import basename, isdir, isfile
from os.path import join as pjoin

from os_utils.os_utils import listdir
from PyTorrentInfo.torrentParser import TorrentParser as TP

debug = True


def get_filenames(tfile_path):
    """
    return a list of filenames inside the passed info dict.

    the 'files' key only exists if it's a dir.
    """
    tp_info = TP().readFile(tfile_path)['torrent']['info']

    if 'files' in tp_info:
        # f['path'] is a list - check this assumption on later bugs
        return [basename(f['path'][0]) for f in tp_info['files']]

    return [tp_info.get('name')]


def find_tfiles(paths, tfilesdir):
    files_tfiles = gen_map(tfilesdir)

    return [tfile_from_filename(path, tfilesdir, files_tfiles) for path in paths]


def tfile_details(tfile_path):
    files_tfile = {}
    try:

        for filename in get_filenames(tfile_path):
            files_tfile[filename] = tfile_path

    except Exception as _e:
        pass

    return files_tfile


def gen_map(tfilesdir):
    tfiles = [pjoin(tfilesdir, f) for f in listdir(tfilesdir) if f.endswith('torrent')]

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
