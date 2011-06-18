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

def edit_removelist(filename,fileext_filename):
	the_list = read_list(filename)
	the_list.sort()
	the_item = optionator("Enter index to remove an item, or type something new to add", the_list )

	if the_item in the_list:
		print "Removing ", the_item	
		remove_from_list(the_item, filename)
	else:
		# check if it's a file extension	
		if the_item in get_fileext_list(fileext_filename):
			print 'Can\'t add file extensions to the remove list'
		else:
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


def get_fileext_list(filename):
	contents = read_list(filename)
	ext_list = [ i.extension for i in contents ]
	
	return ext_list

def edit_filetypelist(filename):
	contents = read_list(filename)
	ext_list = [ i.extension for i in contents ]
	
	index,item = boptionator("Enter index to remove an item, or type something new to add", ext_list )

	if index > 0:
		print "Removing ", item	
		del contents[index]
		write_list(contents,filename)
	else:
		print "Adding ", item
		
		type = optionator("What type of data is it?(or closest by filesize)", ['movie','music','text'])
		if type == 'movie':
			goodsize = 5120
		elif type == 'music':
			goodsize = 100
		else:
			goodsize = 0
		
		new_ext = filetype(item,goodsize)
		
		add_to_list(new_ext, filename)
	

def main():
	
	(options, args) = parse_args()
	
	removelist=os.path.expanduser("~/doc/scripts/torrentbox-scripts/retorrent_include/removelist.list")
	fileext_obj_list = os.path.expanduser('~/doc/scripts/torrentbox-scripts/retorrent_include/fileext_obj.list')



	if options.removelist:
		edit_removelist(removelist,fileext_obj_list)
	elif options.filetypes:
		edit_filetypelist(fileext_obj_list)
	else:	
		print 'Must supply an option'	





if __name__ == "__main__":
	try:
		output = main()
	except KeyboardInterrupt:
		pass

