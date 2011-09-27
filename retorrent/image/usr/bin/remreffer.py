#!/usr/bin/python
import os
from subprocess import Popen
from optparse import OptionParser



def main():

	p = OptionParser()

	p.add_option('-p', '--pretend',
		help='Print actions, then return',
		action='store_true',
		dest='pretend',
		default=False)

	opts,args = p.parse_args()
	
	args = trim_trailing_slashes(args)

	
	print "Would delete:"
	pathlist = []
	for item in args:
		pathlist.extend(add_item(item))	
	
	for item in pathlist:
		print item

	command = ['rm','-Irv']
	command.extend(pathlist)	

	p = Popen(command)
	sts = os.waitpid(p.pid, 0)[1]

def add_item(item):
	pathlist = []

	
	# add the item. if it's a symlink, add the symlink	
	if os.path.exists(item):	
		pathlist.append(os.path.abspath(item))

	if os.path.islink(item):
		# add the real item
		if os.path.exists(os.path.realpath(item)):	
			pathlist.append(os.path.abspath(os.path.realpath(item)))

	# isdir(symlink) == True	
	if os.path.isdir(item):
		for subitem in os.listdir(item):
			pathlist.extend(add_item(os.path.join(item,subitem)))
	
	pathlist.reverse()

	return pathlist

def trim_trailing_slashes(args):
	args = [ arg[0:-1] if arg[-1] == '/' else arg for arg in args  ]

	return args


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
