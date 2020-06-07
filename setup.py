#!/usr/bin/env python

from setuptools import setup
import sys

supported = (3, 4)
if sys.version_info[0:2] < supported:
    out = 'This codebase only supports python >= {}.{}'.format(*supported)
    raise Exception(out)

setup(
    name='retorrent',
    version='0.3',
    description='retorrent - media managment',
    author='jbo',
    author_email='jamesbroadhead@gmail.com',
    url='https://github.com/jamesbroadhead/retorrent.git',
    packages=['coreutils', 'retorrent', 'retorrent.entry_points', 'os_utils', 'redecorators'],
    package_dir={'': 'lib'},
    data_files=[('/usr/share/retorrent', [
        'conf/divider_symbols.conf', 'conf/fileext_details.json', 'conf/retorrentconf.py_skel'
    ])],
    scripts=['bin/seedme',],
    entry_points={
        'console_scripts': [
            'find_tfile =  retorrent.entry_points.find_tfile:main',
            'fix_seed =  retorrent.entry_points.fix_seed:main',
            'is_seeded =   retorrent.entry_points.is_seeded:main',
            'print_tfile = retorrent.entry_points.print_tfile:main',
            'remreffer =   retorrent.entry_points.remreffer:main',
            'retorrent =   retorrent.entry_points.retorrent_main:main',
            'rm_seeded =   retorrent.entry_points.rm_seeded:main',
            'symlinker =   retorrent.entry_points.symlinker:main',
            'unseed_broken = retorrent.entry_points.unseed_broken:main',
        ],
    },
    include_package_data=True,
    zip_safe=False)
