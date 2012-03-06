#!/usr/bin/python
import os
import sys

stripsymbols = ' \n'

# TODO: Logic here to avoid adding file extensions to the removelist :(
# TODO: What else is illegal input?
def add_to_list(the_item,filepath):
	the_list = read_list(filepath)
	
	the_item = the_item.strip(stripsymbols)

	if the_list.count(the_item) ==  0:
		the_list += [ the_item ]
		write_list(the_list, filepath)
	return

""" Pre-removal commenting
def remove_from_list(the_item, filepath):
	the_list = read_list(filepath)
	
	# nicely takes cares of duplicates that might slip in
	while the_list.count(the_item) >  0:
		del the_list[the_list.index(the_item)]
		write = True	
	
	if write: 
		write_list(the_list, filepath)
	
	return
"""	

def write_list(the_list,filepath):
	the_file = open(filepath, 'w')
	the_list.sort()	
	
	for elem in the_list:
		the_file.write(elem + '\n')
	
	the_file.close()
	return

def read_list(filepath):
	if not os.path.exists(filepath):	
		return []	
	the_file = open(filepath, "r")
	the_list = [ elem.strip(stripsymbols) for elem in the_file.readlines() ]
	the_file.close()

	return the_list
