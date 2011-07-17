#!/usr/bin/python
from confparse import *
from os_utils import *

def main():
	folderopts = parse_folderconfig()	

	for folderopt in folderopts:
				
		category_home = folderopt['home']	
		mkdir_p(category_home)
		print 'Considering : ', category_home
	
		removed = []
		# remove broken symlinks 
		for elem in os.listdir(category_home):
			elem_path = os.path.join(category_home,elem)	
			if not os.path.islink(elem_path):
				print 'Raw file detected -- only symlinks should be in cat. home dirs. ', elem		
				
			else:
				if os.path.lexists(elem_path) and not os.path.exists(elem_path):
					print 'Broken symlink! Removing.', elem
					removed += [elem]	
					os.remove(elem_path)

		# make new ones
		for content_dir in folderopt['paths']:
			#print 'Looking at... ',content_dir	
			if not os.path.exists(content_dir):
				print 'A content dir is missing! Creating ... ',content_dir
				mkdir_p(content_dir)

			for content in os.listdir(content_dir):
				#print 'Movie: ',content	
				
				content_path = os.path.abspath(os.path.join(content_dir,content))
				symlink_path = os.path.abspath(os.path.join(category_home,content))
				
				if not os.path.exists(symlink_path):
					os.symlink(content_path,symlink_path)
					if content in removed:
						print 'Replaced a broken symlink',content
				elif not os.path.realpath(symlink_path) ==\
						os.path.realpath(content_path):
					print 'Duplicate content found! ',content,' in \n(==>)',os.path.dirname(os.path.realpath(symlink_path)),' and also \n     ', content_dir 
							
				else:
					# the symlink exists + points at this content :D
					pass


if __name__ == '__main__':
	main()
