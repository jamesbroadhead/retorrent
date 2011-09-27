#!/usr/bin/python
import os 
import sys

from seededlib import is_seeded

def main():
	if len(sys.argv) < 2 :
		print "You must give an argument!"
		return 

	args = sys.argv[1:]

	seeded,unseeded = is_seeded(args)
	
	print "Seeded:"
	for i in seeded:
		print "\t", i
	print "Unseeded:"
	for j in unseeded:	
		print "\t", j
	
	# nothing is unseeded - is_seeded returns true
	if not unseeded:
		return 0
	else:
		return 1

if __name__ == '__main__':
	try:
		returncode = main()
		sys.exit(returncode)
	except KeyboardInterrupt:
		pass
