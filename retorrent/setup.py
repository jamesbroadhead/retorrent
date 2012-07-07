#!/usr/bin/env python

from distutils.core import setup 

setup(name='retorrent',
	version='0.1',
	description='retorrent - media managment',
	author='jbo',
	author_email='jamesbroadhead@gmail.com',
	url='http://code.google.com/p/jamesbroadhead',
	packages = ['retorrentlib', 'os_utils', 'logdecorators'],
	package_dir = {'': 'lib'},
	data_files=[ ('share/retorrent', 
					['conf/divider_symbols.conf', 
					 'conf/fileext_details.conf', 
					 'conf/retorrent.conf_skel'])],
	scripts=['bin/is_seeded.py',
			 'bin/remreffer.py',
			 'bin/retorrent.py',
			 'bin/symlinker.py']
	)
