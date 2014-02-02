#!/usr/bin/env python

from distutils.core import setup

setup(name='retorrent',
    version='0.1',
    description='retorrent - media managment',
    author='jbo',
    author_email='jamesbroadhead@gmail.com',
    url='http://code.google.com/p/jamesbroadhead',
    packages = ['retorrentlib', 'os_utils', 'redecorators'],
    package_dir = {'': 'lib'},
    data_files=[ ('share/retorrent',
                    ['conf/divider_symbols.conf',
                     'conf/fileext_details.json',
                     'conf/retorrentconf.py_skel'])],
    scripts=[
        'bin/find_tfile',
        'bin/is_seeded',
        'bin/remreffer',
        'bin/retorrent',
        'bin/seedme',
        'bin/symlinker']
    )
