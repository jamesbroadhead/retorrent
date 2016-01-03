"""
WIP - this is incomplete and non-functional

Usage:
    documentary.py FILES...
"""
from collections import defaultdict
import os.path
from os.path import join as pjoin

from docopt import docopt
from bs4 import BeautifulSoup

from retorrentlib.confparse import home_config_dir, get_torrentfilesdir
from retorrentlib.engname import to_storage_name
from retorrentlib.find_tfile import find_tfiles

class EpInfo(object):
    def __init__(self, year, tvdb_epno, epname_eng):
        self.year = year
        self.tvdb_epno = tvdb_epno
        self.epname_eng = epname_eng

def get_tfiles_map(filenames):
    files = [ f for f in filenames if os.path.isfile(f) ]
    tfiles = find_tfiles(files, get_torrentfilesdir())
    return { f: t for f, t in zip(files, tfiles) }

def get_web_content(shortname):
    filepath = pjoin(home_config_dir, shortname)
    with open(filepath) as fh:
        return fh.read()

def load_page(content):
    by_series = defaultdict(lambda: defaultdict(dict))
    by_name = defaultdict(lambda: defaultdict(dict))

    soup = BeautifulSoup(content, 'lxml')
    rows = soup.findAll('tr')[5:-4]

    for row in rows:
        tds = row.findAll('td')
        year_tvdbepno = tds[0].getText()
        epname_eng = tds[1].getText().strip()

        year = year_tvdbepno.split('x')[0].strip()
        tvdb_epno = year_tvdbepno.split('x')[1].strip()

        by_series[year][tvdb_epno] = epname_eng
        by_name[to_storage_name(epname_eng)] = EpInfo(year, tvdb_epno, epname_eng)

    return by_series, by_name

def main(files):
    # pylint: disable=unused-variable
    files_tfiles = get_tfiles_map(files)
    assert files_tfiles # silence pyflakes, pylint
    # get the canonical episode numbers from the web
    c = get_web_content('foo')
    by_series, by_name = load_page(c)

    # map the filename / torrent title -> the canonical episode number

    # move and symlink

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args['FILES'])
