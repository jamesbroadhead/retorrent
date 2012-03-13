#!/usr/bin/python
# Author: James Broadhead jamesbroadhead@gmail.com

import logging
import os
import sys
import string

from retorrentlib import retorrenter, confparse

from optparse import OptionParser
from subprocess import Popen, PIPE
from zlib import compress

def main():
	
	options, args = parse_args()

	if options.debug:
		logging.basicConfig(level=logging.INFO)
	
	print options.configdir

	config = { 'retorrentconf_folderopts': 
			confparse.parse_retorrentconf(options.configdir),
		'parse_fileext_details':	
			confparse.parse_fileext_details(options.configdir),
		'parse_divider_symbols':	
			confparse.parse_divider_symbols(options.configdir),
		'find_removelist':	
			confparse.find_removelist(options.configdir)}

	# TODO : proper logging, remove the options.debug arg
	r = retorrenter.retorrenter(config,debug=options.debug)	
	
	seed_torrentfiles = []
	
	# get args (folders / files which are 100% downloaded.
	output = []	
	for i in args:
		output += [r.handle_arg(i)] 
	
	run_and_check(r,output)

	blanks = [ '', None ]
	
	torrentfiles = [ item['torrentfile'] for item in output if \
			not item['torrentfile'] in blanks ]
	
	if len(torrentfiles) > 0:
		print "Don't forget to start these in rtorrent-seed!"
		for item in torrentfiles: 	
			print '\t', item


def run_and_check(r,output):

	for out in output: 
		for cmd in out['commands']:
			os.system(cmd)
		check_symlinks(r,out['symlinks'])

def check_symlinks(r,symlinks):
	output = r.check_symlinks(symlinks)	
	if not output['success']:
		for symlink in output['broken']:
			print "!!!! " +  symlink + " is a broken symlink."
		print "Broken symlinks - fix them then start the torrentfile"
		print "Torrentfile: \t", output['torrentfile']
		print 'Commands issued:'
		for command in commands:
			print '>> ', command
	
		sys.exit("Broken Symlinks - bailing!")

def parse_args():
	parser = OptionParser()
	
	parser.add_option('-c', '--config-dir',
                    help='Specify alternate config dir',
                    dest='configdir',
                    default='')

	parser.add_option('-d', '--debug',
                    help='Print debug messages (where implemented)',
                    action='store_true',
                    dest='debug',
                    default=False)

	options, args = parser.parse_args()

	return options, args

def print_optionstructions():
	print
	print '<WORD> will remove WORD this time only'
	print '"-<WORD> will add WORD to the REMOVE_LIST'
	print '"+<WORD>" will set the dir to be WORD'
	print 	
		

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass
