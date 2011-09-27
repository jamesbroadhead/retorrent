#!/usr/bin/python
# Author: James Broadhead jamesbroadhead@gmail.com

# Bugs? Send me a zip with empty files with the same filenames as the directory tree that failed 

# TODO: Deal with .mkv%09 and .avi.1
# TODO: Handle filename overlap  
#	Current behaviour: Use mv --no-clobber. 
#	Better would be: Detect overlap in filenamer + pick another / ask. 
#	or 				 Detect overlap at question time + ask

# Retorrent needs a few 'helper' files. They are in this dir.
RETORRENT_INCLUDE="~/.retorrent"
# Elements of a filename that should be removed.
# (Anything that isn't a checksum that's in braces({[ is removed automatically)
REMOVE_LIST_FILENAME="removelist.list"


# =============================================================================
# If you make other changes, let me know. I know it's a bit of a mess
# =============================================================================

import os
import sys
import string

from difflib import SequenceMatcher
from optparse import OptionParser
from subprocess import Popen, PIPE
from zlib import compress

from confparse import *
from debugprinter import debugprinter
from filenamer import filenamer
from include_types import *
from list_controller import read_list, filetype
from optionator import *
from os_utils import *

# ==================================================

REMOVE_LIST_FILE=os.path.expanduser(os.path.join(RETORRENT_INCLUDE,REMOVE_LIST_FILENAME))

# ==================================================

def main():
	
	options, args = parse_args()
	
	r = retorrenter(options.debug)	
	
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

	parser.add_option('-d', '--debug',
                    help='Print debug messages (where implemented)',
                    action='store_true',
                    dest='debug',
                    default=False)

	options, args = parser.parse_args()

	return options, args


class retorrenter:
	def __init__(self,debug):
		
		retorrentconf, folderopts = parse_retorrentconf()
		
		self.torrentfilesdir = retorrentconf[0]
		self.seeddir = retorrentconf[1]
		self.seedtorrentfilesdir = retorrentconf[2]

		self.folderopts = folderopts

		self.filetypes_of_interest = parse_fileext_details()
		self.divider_symbols = parse_divider_symbols()

		self.null_output = {'commands':[], 'symlinks':[], 'torrentfile':''}
		self.debug = debug
		self.debugprinter = debugprinter(self.debug)
	
		self.reset_env()
		
	def debugprint(self,str,listol=[]):
		self.debugprinter.debugprint(str,listol)
	
	def reset_env(self):
		# The category folder (movies, tv ... )
		self.dest_category = ''
		self.dest_folder = ''
		self.dest_series_folder=''
		# The series or movie-name folder 
		self.dest_dirpath = ''
		
		
		self.filenamer = filenamer(REMOVE_LIST_FILE, self.divider_symbols, \
					self.filetypes_of_interest, \
					the_debugprinter=self.debugprinter) 
	
	def set_num_interesting_files(self,num_interesting_files):
		self.filenamer.set_num_interesting_files(num_interesting_files)

		
	
	def handle_arg(self,argument):
		
		print "|\n|\n|\n|"
		
		if not os.path.exists(argument):
			print 'Can\'t find path: ', argument 
			return self.null_output 

		the_path = os.path.abspath(argument)	
		
		# get a list of files to keep
		# NOTE: These are only those of the interesting files
		orig_paths,orig_foldername,orig_intermeds,orig_filenames,num_discarded_files = self.find_files_to_keep(the_path)
		
		num_interesting_files = len(orig_paths)
		self.filenamer.set_num_interesting_files(num_interesting_files)	

		if len(orig_paths) == 0:
			print "No interesting files found! Skipping!"
			self.reset_env()	
			return self.null_output 

		self.debugprint("Dirpath before autoset: " + self.dest_dirpath)
		
		possible_series_foldernames = [ \
				self.filenamer.convert_filename(orig_filenames[0],True), \
				self.filenamer.convert_filename(orig_foldername,True) ]	
		
		possible_series_foldernames = [ i for i in possible_series_foldernames \
				if not i == '' ]
				
		self.autoset_dest_dirpath(possible_series_foldernames,orig_paths)
		
		self.debugprint('DestFolder after autoset: ' + self.dest_folder)
		self.debugprint("Dirpath after autoset: " + self.dest_dirpath)

		if self.dest_category == "": 
			self.manually_set_dest_category(argument,orig_paths)
			if self.dest_category == "":
				# we are skipping this file.
				print "skipping!"
				self.reset_env()	
				return self.null_output
			else:
				# recurse
				return self.handle_arg(argument)
			
		# At this point, self.dest_category is set. 
		self.filenamer.set_movie(self.is_movie())
		
		if self.dest_folder == '':
			# not enough space :(
			print '!!! Can\'t find enough space in any of that category to proceed!'
			print 'Free some disk space, or add another location.'
			return self.null_output

		self.dest_folder = os.path.expanduser(self.dest_folder)
		self.dest_dirpath = os.path.expanduser(self.dest_dirpath)

		# At this point : self.dest_folder is set. self.dest_dirpath may not be.
		
		if self.dest_category['should_rename']:
			self.debugprint('About to generate dest_dirpath; '+self.dest_dirpath)	
			if self.dest_dirpath == "":
				self.manually_set_dest_dirpath(num_interesting_files, \
						possible_series_foldernames)
				if self.dest_dirpath == "":
					print "Didn't set a directory - failing"
					self.reset_env()	
					return self.null_output

			# At this point, self.dest_dirpath contains the full folder path 
			self.debugprint('Final dest_dirpath=' +self.dest_dirpath)	
			##################################
			## Now to rename the filenames
			##################################
			# create output paths based on the filenames 
			dest_filenames_from_files = [ self.filenamer.convert_filename(\
					os.path.basename(file),False) for file in orig_paths]
			dest_paths_from_files = [ os.path.join(self.dest_dirpath,filename) \
					for filename in dest_filenames_from_files ] 
			
			self.debugprint('',[['dest_filenames_from_files',dest_filenames_from_files],['dest_paths_from_files',dest_paths_from_files]])

			# create output paths based on the folder name (only if given a folder)
			if os.path.isdir(the_path):
				
				if len(possible_series_foldernames) > 1:
					series_foldername_from_orig_foldername = possible_series_foldernames[1]
				# there is no good series foldername. Base off the first filename.
				elif len(possible_series_foldernames) > 0:
					series_foldername_from_orig_foldername = possible_series_foldernames[0]
				else:
					possible_series_foldernames = ['']
					series_foldername_from_orig_foldername = ''

					
				dest_filenames_based_on_folder = [ \
						self.filenamer.gen_final_filename_from_foldername( \
						series_foldername_from_orig_foldername, afile) \
						for afile in dest_filenames_from_files ]
				
				dest_paths_from_folder = [ os.path.join(self.dest_dirpath,file) \
						for file in dest_filenames_based_on_folder ]
				
				self.debugprint('',[['dest_filenames_from_folder',dest_filenames_based_on_folder],['dest_paths_from_folder',dest_paths_from_folder]])

			else:
				# If not given a folder, set to the same as the filename-based output.
				dest_filenames_based_on_folder = dest_filenames_from_files
				dest_paths_from_folder = dest_paths_from_files
			

			# list the differences between the two methods
			list_diff = []
			list_same = []
			for file_item in dest_paths_from_files:
				if not file_item in dest_paths_from_folder:
					list_diff += [(file_item,dest_paths_from_folder[dest_paths_from_files.index(file_item)])]
				else:
					list_same += [(file_item,dest_paths_from_folder[dest_paths_from_files.index(file_item)])]
			
			# prepare the lists for printing, then sort. 
			# Can't sort the orig and dest lists, as they may sort differently
			printable_dest_paths_from_files = [ i for i in dest_paths_from_files ]
			printable_list_diff_file_based = [ i[0] for i in list_diff ]
			printable_list_diff_folder_based = [ i[1] for i in list_diff ]
			printable_list_same = [ i[0] for i in list_same ]
			
			printable_dest_paths_from_files.sort()
			printable_list_diff_file_based.sort()
			printable_list_diff_folder_based.sort()
			printable_list_same.sort()

			##### USER DECIDES BETWEEN RESULTS

			# the two methods produced the same results. Print one, ask y/n
			print 	
			if len(list_diff) == 0:
				for i in printable_dest_paths_from_files:
					print i
				
				question = "Use these filenames or enter new term to remove"
				options = ["filenames", "cancel"]
			
			# the two methods produced different results. (either complete or partial)
			# Print only the differences,  ask 1/2/n
			else:
				if len(printable_list_same) > 0:
					print "The Same:"
					for file in printable_list_same:
						print "\t", file
				print "File-based:"
				for file_based in printable_list_diff_file_based:
					print "\t", file_based
				print "Folder-based:"
				for folder_based in printable_list_diff_folder_based: 
					print "\t", folder_based
				
				question = "Filename-based and Foldername-based produced differences: Select which is better, or enter new term to remove"
				options = ["filenames", "foldernames", "cancel"]
			
			print 
			
			# Possibilities: '-', an option, '', foo (from +foo)
			answer = self.pose_question(question,options)
			
			if answer == '-':
				return self.handle_arg(argument)
			elif answer  == "cancel":
				self.reset_env()	
				return self.null_output	
			elif answer == "filenames":
				dest_paths = dest_paths_from_files
			elif answer == "foldernames":
				dest_paths = dest_paths_from_folder
			elif num_interesting_files == 1: 
				## TODO: Re-attach file ext if ignored	
				
				print 'You ignored our suggestion; taking: "' + answer + '"' 
				dest_paths = [ os.path.join(self.dest_folder,\
						self.dest_dirpath,answer) ]
			else:
				# more than one file
				print 'We don\'t currently support manual mmvs :('
				return self.handle_arg(argument)
		
		else:
			print "Not renaming files"
			self.dest_dirpath = os.path.join(self.dest_folder,orig_foldername)	
			dest_paths = [ os.path.join(self.dest_dirpath,filename) for filename in orig_filenames ]
		
		##### LET'S BUILD SOME COMMANDS!
		commands = []
		torrentfile = ""
			
		# make the dir immediately, for the case show*avi	
		mkdir_p(self.dest_dirpath)	
		
		for dest in dest_paths:
			if os.path.exists(dest):
				print 'Already exists, not moving: ', dest

		commands += [ "mv -nv " + '"' + orig + '"' + " " + '"'+dest+'"' for (orig,dest) in zip(orig_paths,dest_paths) ]
		
		do_seed = optionator("Should these be seeded?" , ['no', 'yes' , '<cancel>'] )
		torrentfile = '' 
		seeddir_paths = []
		# this means '<cancel>'
		if do_seed == "":
			self.reset_env()	
			return self.null_output 
		elif do_seed  == "yes" :
			# link arg to .torrent via optionator
			torrentfile = self.find_torrentfile(the_path)
			
			if not orig_foldername == "":
				commands += [ "mv -nv " + '"'+the_path+'"' + " " + '"'+self.seeddir+'"' ]
			
			if not torrentfile == '':
				# move torrentfile to seeddir
				commands += [ "mv -nv " + '"' + self.torrentfilesdir + "/" + torrentfile+'"' + " " + '"'+self.seedtorrentfilesdir+'"' ]
			
			# gen filenames + foldername for symlinked files
			seeddir_paths = self.gen_seeddir_paths(orig_foldername,orig_intermeds,orig_filenames)
			
			commands += [ "ln -s " + '"'+dest+'"' + " " + '"'+seedpath+'"' for dest,seedpath in zip(dest_paths,seeddir_paths) ]
		else:
			
			# delete remainder of files in torrentdir
			# Don't delete the arg dir if it's the same as the target dir (renaming files in-place)
			dud_files_remaining = num_discarded_files > 0
			only_ever_one_file_in_dir = os.path.isdir(argument) and num_interesting_files == 1 
			dir_is_now_empty = os.path.isdir(argument) and len(os.listdir(argument)) - num_interesting_files == 0
			
			# delete the source if there are remaining dud files / the dir is empty, provided that it's not also the dest
			if (dud_files_remaining or only_ever_one_file_in_dir or dir_is_now_empty) and not os.path.realpath(argument) == os.path.realpath(self.dest_dirpath):
				if dir_is_now_empty:
					commands += [ 'rmdir "' + the_path + '"' ]
				else:	
					# have taken wanted files, delete remaining dir
					the_path = '"' + the_path + '"'	
					
					commands += [ 'echo "Files still in the folder" ' ]
					commands += [ 'ls -aR ' + the_path + '/']
					commands += [ "rm -Irv " + the_path ]
		
		self.reset_env()	
		return { 'commands': commands, 'symlinks': seeddir_paths, 'torrentfile': torrentfile}
		
	def check_symlinks(self, seeddir_paths):	

		# check any symlinks that were created
		broken_syms = []
		for seedpath in seeddir_paths:
			if not os.path.exists(seedpath):
				broken_syms += [seedpath]
	
		if len(broken_syms) > 0 :	
			return { 'success': False, 'broken': broken_syms }	
	
		# We have moved the files, but are not seeding. Return an empty string.
		return { 'success': True } 

	
	# What is the dest_dirpath
	def autoset_dest_dirpath(self,possible_series_foldernames,orig_paths):
		
		self.debugprint('retorrenter.autoset_dest_dirpath(' + ','.join(possible_series_foldernames)+')')

		if self.dest_category == "":
			categories = [ cat for cat in self.folderopts ]	
		else:
			# the dest category is already set from somewhere else
			categories = [ self.dest_category ]
	
		for category in categories:
			for cat_folder in category['paths']:
				for poss_series_folder in possible_series_foldernames:
					possible_path = os.path.expanduser(os.path.join(cat_folder,poss_series_folder))
					self.debugprint('Looking for ' + possible_path)	
					if os.path.exists(possible_path):
						self.dest_category = category

						self.dest_series_folder = poss_series_folder
						if enough_space(orig_paths,possible_path):
							self.dest_folder = cat_folder
							self.dest_dirpath = possible_path 
						else:
							# Not enough space, but we have the series_folder.
							# Lets try another disk, or fail
							self.dest_category['paths'].remove(cat_folder)
							self.autoset_equivalent_dest_folder(orig_paths)	
						return	
	
	def autoset_equivalent_dest_folder(self,orig_paths):
		self.debugprint('Trying to create an eqivalent dest_folder for ' + self.dest_category['category'] + '/' + self.dest_series_folder)

		if self.dest_category and not self.dest_series_folder == "":
			# let's create an equivalent dir on a different drive
			for cat_folder in self.dest_category['paths']:
				possible_path = os.path.join(cat_folder,self.dest_series_folder)
				
				self.debugprint('Checking:' + possible_path)	
				self.debugprint('Equivalent candidate: ' + possible_path)	
				
				if os.path.exists(possible_path) and enough_space(orig_paths,possible_path):
					self.dest_folder = cat_folder
					self.dest_dirpath = possible_path
					return

			for cat_folder in self.dest_category['paths']:
				if enough_space(orig_paths,possible_path):
					self.dest_folder = cat_folder
					self.dest_dirpath = possible_path
					return

			# There are no drives in the list with enough disk space ... :(
			# TODO: Bail here.

		else:
			# we don't have enough info to make the dir on a different drive
			pass	


	def manually_set_dest_category(self,argument,orig_paths):
		category_names = [ cat['category'] for cat in self.folderopts ]	

		question = 	"Destination for " + argument
		dest_category_name = optionator(question, category_names + ["<cancel>"] )
			
		for folderopt in self.folderopts:
			if dest_category_name == folderopt['category']:
				self.dest_category = folderopt
				
				self.autoset_dest_folder_from_dest_category(orig_paths)
				
				return
		
		print 'Error -- category was unrecognised!'
		self.manually_set_dest_category(argument,orig_paths)
	
	def autoset_dest_folder_from_dest_category(self,orig_paths):
		if self.dest_category:	
			for path in self.dest_category['paths']:
				self.debugprint('Possible path: ' + path)
				if not os.path.exists(path):
					print 'Warning: Config contains a path that doesn\'t exist: ' + path
				elif enough_space(orig_paths,path):
					self.debugprint('Setting dest_folder to: '+path)	
					self.dest_folder = path
					return

	def manually_set_dest_dirpath(self,num_interesting_files, \
			possible_series_foldernames):
		
		self.debugprint('retorrenter.manually_set_dest_dirpath()')	
		# gen dest paths from these foldernames
			
		# if a movie has +1 files, need a folder. All else might need a folder
		if self.is_movie() and num_interesting_files == 1:	
			self.debugprint('manually_set_dest_dirpath: This is a movie, no need for a folder')	
			self.dest_dirpath = self.dest_folder	
		else:	
			
			if self.is_movie() or num_interesting_files > 1:
				dirpath_q = "What foldername should we use?"
				dirpath_q_opts = possible_series_foldernames
			else:
				dirpath_q =	"Is this a series? If so, use what folder name?"
				dirpath_q_opts = possible_series_foldernames + [ "" ]
		
			dirpath_ans = self.pose_question(dirpath_q, dirpath_q_opts)

			if not dirpath_ans == '-':
				self.dest_dirpath = os.path.join(self.dest_folder,dirpath_ans)
			else:	
				# a new removeitem has been added - regenerate psf
					
				possible_series_foldernames = [ \
					self.filenamer.convert_filename(item,True) \
					for item in possible_series_foldernames ] 

				self.manually_set_dest_dirpath(num_interesting_files, \
						possible_series_foldernames)
				return
	
	# Note: returns '-' if a recurse is needed
	def pose_question(self,question,options):
		
		answer = eqoptionator(question,options)
		
		if answer in options or answer == '':
			return answer
		elif answer.startswith('+'):
			return answer[1:] 	
		elif answer.startswith('-'):
			self.filenamer.add_to_removelist(answer[1:])
			return '-'
		else:
			self.filenamer.add_extra_removeitem(answer)
			return '-'	
	
	# For all files
	# Needs to return:
	#	Foldername (if arg is torrent/$FOLDER )
	#		orig_foldername neither begins nor ends with slashes	
	#	Intermediate ( torrent/$FOLDER/$INTERMED/ )
	#		elements of orig_intermeds elements have neither beginning nor ending slashes 
	#	Files ( torrent.$FOLDER/$INTERMED/$FILE )
	def find_files_to_keep(self,the_path):
		file_paths = []
		file_names = []
		intermeds = [] 
		# if (folder), figure out which files are the movie
		if os.path.isdir(the_path):
			
			orig_foldername = os.path.basename(the_path)

			for (path,dirs,files) in os.walk(the_path):
				for file in files:
					file_path = path + "/" + file
					thisfile_intermed = path[len(the_path)+1:]
					if os.path.exists(file_path) :
						file_paths += [os.path.abspath(file_path)]
						file_names += [os.path.basename(file_path)]
						intermeds += [thisfile_intermed]
					else:
						print "Internal error - built a path, then file didn't exist(?)"	
		else:
			orig_foldername = "" # it's a file, flat in ~/torrents	
			if os.path.exists(the_path):
				file_path = the_path
				file_paths = [os.path.abspath(file_path)]
				file_names = [os.path.basename(file_path)]
				intermeds = [""]*len(file_names)

		# remove files that aren't of interest
		filepaths_to_keep,intermeds_to_keep,filenames_to_keep,num_discarded_files = self.get_movies_and_extras(file_paths,intermeds,file_names)
		
		return filepaths_to_keep,orig_foldername,intermeds_to_keep,filenames_to_keep, num_discarded_files


	# strip uninteresting files from the lists
	def get_movies_and_extras(self,list_of_filepaths, list_of_intermeds, list_of_filenames):
		
		filepaths_to_keep = []
		intermeds_to_keep = []
		filenames_to_keep = []
		num_discarded_files = 0

		for filepath,intermed,filename in zip(list_of_filepaths,list_of_intermeds, list_of_filenames):	
			if self.is_of_interest(filepath,filename):
				filepaths_to_keep += [filepath]
				intermeds_to_keep += [intermed]
				filenames_to_keep += [filename]
			else: 
				print "Skipping ",os.path.basename(filepath)
				num_discarded_files += 1

		return filepaths_to_keep,intermeds_to_keep,filenames_to_keep,num_discarded_files 

	def is_of_interest(self,file_path, filename):
		self.debugprint('retorrenter.is_of_interest(' + file_path + ',' + filename + ')')
		
		
		(path,extension) = os.path.splitext(file_path)
		# trim the . from the extension for matching
		extension = extension[1:].lower()	
		
		for foi in self.filetypes_of_interest:
			if extension == foi['fileext']:
				# if the filename has something which excludes it, skip it
				# eg. 'sample'	
				for exclude in foi['ignore_if_in_filename']:
					if exclude == '':
						continue
					if not filename.lower().find(exclude.lower()) == -1:
						# this file has a phrase which excludes it
						self.debugprint(filename + ' contains a phrase which excludes it')	
						return False 
				filestat = os.stat(file_path)
				# this will actually get the size of all the blocks, not the space used.
				# Close enough ... :P
				disk_filesize_kB = filestat.st_blocks*filestat.st_blksize/(8*1024)
				
				if disk_filesize_kB > foi['goodsize']:
					return True
				else:
					self.debugprint('Size:' + str(disk_filesize_kB) +  'kB <' + str(foi['goodsize']) +'kB for:' + file_path)
		self.debugprint(filename + ' didn\'t trigger any interest ...')
		return False
	
	def is_movie(self):
		if self.dest_category:	
			return self.dest_category['treat_as'] == 'movies'
		return False

	# TODO: Remove tfiles already picked during other options. 
	def find_torrentfile(self,the_path):
		# get the file / foldername (not necc. the same as the arg itself
		split_path = the_path.rsplit('/')	
		arg_name = split_path[-1]
		
		the_torrentfiles =  os.listdir(self.torrentfilesdir) 
		
		tfiles = []
		for tfile in the_torrentfiles:
			cf = self.filenamer.convert_filename(tfile.rstrip('torrent').rstrip('.'),True,interactive=False) 	
			score = SequenceMatcher('',str2utf8(arg_name),str2utf8(cf)).ratio()
		
			tfiles += [{'filename':tfile, 'conv_filename':cf, 'score':score } ]

		
		tfiles = sorted(tfiles, compare_scores)

		chosen_torrentfile = optionator('For: '+arg_name,[ t['filename'] for t in tfiles] )

		return chosen_torrentfile
	
	def gen_seeddir_paths(self,orig_foldername,orig_intermeds,orig_filenames):
			
		return [ self.seeddir + "/" + orig_foldername + "/" + intermeds + '/' + filename for intermeds,filename in zip(orig_intermeds,orig_filenames) ] 


def compare_scores(A,B):
	return cmp(B['score'],A['score'])


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
