#!/usr/bin/python

import os

from os_utils import os_utils 
from retorrentlib import confparse

def main():
	foo,folderopts = confparse.parse_retorrentconf()	

	for folderopt in folderopts:
				
		category_home = folderopt['home']	
		os_utils.mkdir_p(os.path.expanduser(category_home))
		print 'Considering : ', category_home
	
		removed = []
		# remove broken symlinks 
		for elem in os.listdir(category_home):
			elem_path = os.path.join(category_home,elem)	
			
			if not os.path.islink(elem_path):
				
				if not len(os.listdir(elem_path)):
						os.rmdir(elem_path)
				else:
					for f in os.listdir(elem_path):
						if not os.path.islink(os.path.join(elem_path,f)):
							print 'Non-symlinked file detected in folder', elem_path
							print '\t Non-symlinked folders should only contain symlinks'
				# TODO: Descend into dir, remove broken symlinks. 
			else:
				if os.path.lexists(elem_path) and not os.path.exists(elem_path):
					print 'Broken symlink! Removing.', elem
					removed += [elem]	
					os.remove(elem_path)
		
		if category_home in folderopt['paths']:
			print 'The content home is in the list of content paths. Cannot continue.'
			continue

		# make new ones
		for content_dir in folderopt['paths']:
			#print 'Looking at... ',content_dir	
			if not os.path.exists(content_dir):
				#print 'A content dir is missing! Please create:',content_dir
				continue	
			
			for content in os.listdir(content_dir):
				
				# content can either be movie.avi or series.name/
				content_path = os.path.abspath(os.path.join(content_dir,content))
				symlink_path = os.path.abspath(os.path.join(category_home,content))
				# link directly if symlink doesn't exist
				if not os.path.exists(symlink_path):
					os.symlink(content_path,symlink_path)
					if content in removed:
						print 'Replaced a broken symlink',content

				# symlink with same name already exists
				# 	and doesn't point to same location
				elif os.path.islink(symlink_path) and \
					not os.path.realpath(symlink_path) == \
						os.path.realpath(content_path):
					
					oldlink_realpath = os.path.realpath(symlink_path)
					
					# they're both links to different directories
					#	create dir, populate with symlinks to the content 
					#	in both
					if os.path.isdir(oldlink_realpath) and \
							os.path.isdir(content_path):
						# remove oldlink
						os.remove(symlink_path)	
						# mkdir foo
						os_utils.mkdir_p(symlink_path)
						
						link_contents(oldlink_realpath,symlink_path)
						link_contents(content_path,symlink_path)
					else:
						print 'Duplicate files, can\'t combine :('
						print '\t',oldlink_realpath
						print '\t',content_path
				
				# dir found in category_home. 
				#	Broken symlinks and empty dirs should be gone already
				#	TODO: Populate with symlinks to files in content dir 
				elif not os.path.islink(symlink_path) and \
						os.path.isdir(symlink_path):
					print 'Found multiple dirs ', content
					pass	
				else:
					# the symlink exists + points at this content :D
					pass

	
def link_contents(content_path,linkdir_path):
	content_realpath = os.path.realpath(content_path)	
	for fn in os.listdir(content_realpath):
		f_realpath = os.path.join(content_realpath,fn)
		f_sympath = os.path.join(linkdir_path,fn)

		if not os.path.exists(f_sympath):
			os.symlink(f_realpath,f_sympath)
		elif os.path.exists(f_sympath) and \
				not os_utils.sym_sametarget(f_sympath,f_realpath):
			print 'Duplicate content found for ',f_sympath,' in'
			print '==>', os.path.realpath(f_sympath)
			print '   ', os.path.realpath(f_realpath)
		else:
			# symlink exists, but points to same location.
			pass

if __name__ == '__main__':
	main()
