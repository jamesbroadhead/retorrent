#!/usr/bin/python
import os
import sys
import pickle

from optparse import OptionParser

from include_types import *
from optionator import boptionator,optionator

def parse_args():
	parser = OptionParser()
	
	parser.add_option('-d', '--debug',
                    help='Print debug messages (where implemented)',
                    action='store_true',
                    dest='debug',
                    default=False)

	parser.add_option('-r', '--removelist',
                    help='Edit the removelist',
                    action='store_true',
                    dest='removelist',
                    default=False)

	parser.add_option('-f', '--filetype',
                    help='Edit list of filetypes',
                    action='store_true',
                    dest='filetypes',
                    default=False)
	
	return parser.parse_args()

def edit_removelist(filename):
	the_list = read_list(filename)
	the_list.sort()
	the_item = optionator("Enter index to remove an item, or type something new to add", the_list )

	if the_item in the_list:
		print "Removing ", the_item	
		remove_from_list(the_item, filename)
	else:
		if len(the_item) == 1 or the_item == '1ch': 
			print 'refusing!'
			return
		print "Adding ", the_item
		add_to_list(the_item, filename)
	
	the_list = read_list(filename)

	print "List now reads:"	
	print the_list

	return


# these have file i/o so they can be called externally
# TODO: Logic here to avoid adding file extensions to the removelist :(
def add_to_list(the_item,filename):
	the_list = read_list(filename)

	if the_list.count(the_item) ==  0:
		the_list += [ the_item ]
		write_list(the_list, filename)
	return

# these have file i/o so they can be called externally
def remove_from_list(the_item, filename):
	the_list = read_list(filename)

	if the_list.count(the_item) >  0:
		del the_list[the_list.index(the_item)]
		write_list(the_list, filename)
	return
		
def write_list(the_list,filename):
	the_file = open(filename, 'w')
	the_list.sort()	
	pickle.dump(the_list,the_file)
	the_file.close()
	
	return

def read_list(filename):
	the_file = open(filename, "r")
	the_list = pickle.load(the_file)
	the_file.close()

	return the_list


def main():
	
	(options, args) = parse_args()
	
	removelist=os.path.expanduser("~/.retorrent/removelist.list")

	if options.removelist:
		edit_removelist(removelist)
	else:	
		print 'Must supply an option'	





if __name__ == "__main__":
	try:
		output = main()
	except KeyboardInterrupt:
		pass

