#!/usr/bin/python
import os
import sys

import confparse

def read_list():
	filepath = confparse.find_removelist()

	stripsymbols = ' \n'
	
	# don't catch - retorrent can't function without a removelist
	with open(filepath) as f:
		rmlist = [ elem.strip(stripsymbols) for elem in f.readlines() ]
		
	return rmlist


def write_list(rmlist,filepath):
	filepath = confparse.find_removelist()

	rmlist = [ i.append('\n') for i in rmlist ]	
	rmlist.sort()	
	
	with open(filepath,'w') as f:
		f.writelines(rmlist)
		os.fsync(f)

# TODO: What else is illegal input?
def add_and_sync(rmlist,item):

	# make sure it's not a file extension
	fileext_list = confparse.read_fileexts()
	if item and not string.strip(item,' .') in fileext_list:
		rmlist.append(item)
	
	rmlist = set(rmlist)
	
	write_list(the_list, filepath)
	return rmlist



