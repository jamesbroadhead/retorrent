#!/usr/bin/env python

from distutils.core import setup

setup(name='retorrent',
	version='0.1',
	description='retorrent - media managment',
	author='jbo',
	author_email='jamesbroadhead@gmail.com',
	url='http://code.google.com/p/jamesbroadhead',
	packages=['retorrent'],
	package_dir = {'': 'lib'},
	scripts=['bin/is_seeded.py',
			 'bin/list_controller.py',
			 'bin/remreffer.py',
			 'bin/retorrent.py',
			 'bin/symlinker.py']
	)
