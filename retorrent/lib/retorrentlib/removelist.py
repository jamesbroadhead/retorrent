#!/usr/bin/python

import os
import string
import sys

import confparse

def read_list():
	filepath = confparse.find_removelist()

	stripsymbols = ' \n'
	
	# don't catch - retorrent can't function without a removelist
	with open(filepath) as f:
		rmlist = [ elem.strip(stripsymbols) for elem in f.readlines() ]
		
	return rmlist


def write_list(rmlist):
	filepath = confparse.find_removelist()

	rmlist_out = [ i+'\n' for i in rmlist ]	
	rmlist_out.sort()	
	
	with open(filepath,'w') as f:
		f.writelines(rmlist_out)
		os.fsync(f)

# TODO: What else is illegal input?

def add_and_sync(rmlist,item):

	# make sure it's not a file extension
	fileext_list = confparse.read_fileexts()
	
	rmlist = set(rmlist)
	if item and not string.strip(item,' .') in fileext_list:
		rmlist.add(item)
	
	write_list(rmlist)
	return rmlist



