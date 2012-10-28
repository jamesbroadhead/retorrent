#!/usr/bin/ipython

import os
import string

import removelist
import os_utils

from debugprinter import debugprinter
from episoder import episoder
from logdecorators.tracelogdecorator import tracelogdecorator
from logdecorators.tracelogdecorator import tracelogdecorator

hexdigits = "0123456789abcdefABCDEF"
openbraces = [ "[" , "{", "(" ] 
closebraces = [ "]", "}", ")" ] 
	


class filenamer:
	
	def __init__(self, divider_list , filetypes_of_interest, the_debugprinter=debugprinter(False)):
		
		self.remove_list = removelist.read_list()
		self.tmp_remove_list = []
		
		self.divider_list = divider_list
		self.fileext_list = [ f['fileext'] for f in filetypes_of_interest ] 

		self.the_episoder = episoder(the_debugprinter)
		self.debugprinter = the_debugprinter
		
		self.is_movie = False

	def debugprint(self, str, listol=[]):
		self.debugprinter.debugprint(str,listol)
	
	def add_to_removelist(self,item):
		self.remove_list = removelist.add_and_sync(self.remove_list,item)

	def set_num_interesting_files(self,num_interesting_files):
		self.the_episoder.set_num_interesting_files(num_interesting_files)

	def set_movie(self, is_movie):
		self.is_movie = is_movie	
		self.the_episoder.set_movie(is_movie)
	
	def convert_filename(self, filename,is_foldername,interactive=True):
		self.the_episoder.interactive = interactive
		
		#if interactive:
			#print 'Examining: ' + filename	
		if filename == '':
			self.debugprint('Not converting blank filename!',[])
			return ''
		self.debugprint('filenamer.convert_filename(' + filename + ', is_foldername==' + str(is_foldername) + ')')

		filename = self.remove_divider_symbols(filename)
		
		self.debugprint('filenamer.convert_filename, after self.remove_divider_symbols : ' + filename )

		# remove braces from anything that isn't a checksum
		filename = self.sort_out_braces(filename, is_foldername)
		
		self.debugprint('filenamer.convert_filename, after self.sort_out_braces: ' + filename )

		# Apparently, there are things called 'zero width spaces'. Remove them.
		filename = self.remove_zwsp(filename)
	
		self.debugprint('filenamer.convert_filename, after filenamer.remove_zwsp: ' + filename )

		# change CamelCase to Camel.Case
		filename = self.remove_camelcase(filename)
		
		self.debugprint('filenamer.convert_filename, after filenamer.remove_camelcase: ' + filename )
		
		filename = self.add_necc_dots(filename)
		
		self.debugprint('filenamer.convert_filename, after filenamer.add_necc_dots: ' + filename )
		
		filename_split = filename.split('.')
		filename_split = self.to_lowercase(filename_split)
		
		self.debugprint('filenamer.convert_filename, after filenamer.to_lowercase: ' + '[' + ', '.join(filename_split) + ']')
		
		filename_split = self.remove_extra_details(filename_split, self.remove_list)
		filename_split = self.remove_extra_details(filename_split, self.tmp_remove_list)
	
		self.debugprint('filenamer.convert_filename, after filenamer.remove_extra_details(removelist): ' + '[' + ', '.join(filename_split) + ']')
		
		# pre-2012 Don't want years tangling the episoder. 
		# pre-2012 Doesn't work well either way, this is better 					#				than the opposite 
		# 2012-03 Episoder needs to know about years, as they may have 
		#				been preserved by filenamer. Therefore, episoder 
		#				handles all year info now.
		#filename_split = self.remove_years(filename_split)
			
		#self.debugprint('filenamer.convert_filename, after episoder.remove_years: ' + '[' + ', '.join(filename_split) + ']')

		# Detect and Convert episode numbers. 
		# NEW! Movies have cd01,cd02-so they go through episoder
		filename_split,epno_index = self.the_episoder.add_series_episode_details(filename_split,is_foldername)
		
		self.debugprint('filenamer.convert_filename, after episoder.add_series_episode_details: ' + '[' + ', '.join(filename_split) + ']')
		
		if is_foldername:
			# don't want file extensions in a folder name
			filename_split = self.remove_extra_details(filename_split,self.fileext_list)
			self.debugprint('filenamer.convert_filename, creating a folder name, so : after filenamer.remove_extra_details(file_extensions): ' + '[' + ', '.join(filename_split) + ']')
	
		if not self.is_movie:
			filename_split = self.remove_following_text(filename_split,epno_index, is_foldername)
			self.debugprint('filenamer.convert_filename, not a movie (no episode number) so: after filenamer.remove_following_text: ' + '[' + ', '.join(filename_split) + ']')
	

		# remove any empty elements from the filename	
		filename_split = self.remove_empty_elements(filename_split)
		
		self.debugprint('filenamer.convert_filename, after filenamer.remove_empty_elements: ' + '[' + ', '.join(filename_split) + ']')
		
		filename = ".".join(filename_split)
		
		self.debugprint('filenamer.convert_filename RETURNING:' + filename)
		return filename

	# get TITLE from foldername
	# get EPNO,FILEEXT from filename
	# Make: TITLE.EPNO.FILEEXT	
	def gen_final_filename_from_foldername(self,the_dirpath, filename):
		self.debugprint('filenamer.gen_final_filename_from_foldername(the_dirpath=' + the_dirpath + ', filename=' + filename + ')')		
		
		# GET EPNO from filename
		# run convert_filename on filename as a filename. Then pull epno
		filename = self.convert_filename(filename,is_foldername=False)
		self.debugprint('converted the filename to: ',filename)	
		epno = self.the_episoder.get_good_epno(filename)
		fileext = self.find_fileext(filename)	
		
		# Get Title from Foldername
		#foldername = os_utils.get_foldername(the_dirpath)
		newfilename = self.convert_filename(the_dirpath,is_foldername=True)
		
		self.debugprint('filenamer.gen_final_filename_from_foldername: Got: filename=' + filename + ' epno=' +epno+ ' fileext=' + fileext)

		# join. We've lost the file ext ... 
		filename_out = '.'.join((newfilename,epno,fileext))
		filename_out = self.remove_dupe_dots(filename_out)	

		output = os.path.join(os.path.dirname(the_dirpath.strip('/')),filename_out)

		return output 

	# removes Zero Width Spaces from a string. 
	# Returns in UTF-8. HERE BE DRAGONS 
	def remove_zwsp(self,filename):
	
		if type(filename) == type(u'unicode'):
			ufilename = filename
		else:
			ufilename = unicode(filename,'utf-8', errors='ignore')	
		
		zwsp = u'\u200b'

		while zwsp in ufilename:
			ufilename = ufilename[0:ufilename.find(zwsp)] + ufilename[ufilename.find(zwsp)+len(zwsp):]

		#filename = ufilename.encode()

		return ufilename
	
	def remove_camelcase(self, filename):
		if len(filename) == 0:
			return filename 
		outfilename = ""	
		old = filename[0]
		outfilename += old
		for curr in filename[1:]:
			if old.islower() and curr.isupper():
				outfilename += "."		
			old = curr
			outfilename += curr
		return outfilename  

	def add_necc_dots(self, filename):
		divide_items = ["["]
		for item in divide_items:
			if item in filename:
				index = filename.find(item)
				while not index == -1:
					if not index == 0 and not filename[index-1] == ".":
						filename = filename[0:index] + "." + filename[index:]
					# index + 2 is the next char after the item
					index = filename[index+2:].find(item)
		
		return filename
	
	def remove_dupe_dots(self,filename):
		filename = filename.strip('.')
		
		ddot_index = filename.find("..")
		while not ddot_index == -1:
			filename = filename[0:ddot_index] + filename[ddot_index+1:]
			ddot_index = filename.find("..")	

		return filename	

	def to_lowercase(self, filename_split):
		# look for a checksum. Lowercase everything else
		for index,item in enumerate(filename_split):
			if not is_checksum(item):
				filename_split[index] = item.lower()
		return filename_split


	def remove_empty_elements(self, filename_split):
		return [ item for item in filename_split if not item == '' ]	
		

	def remove_divider_symbols(self, filename):
		
		for symbol in self.divider_list:
			if symbol in filename:
				filename = filename.replace(symbol,".")
		return filename

	def remove_camelcase(self, filename):
		if len(filename) == 0:
			return filename 
		outfilename = ""	
		old = filename[0]
		outfilename += old
		for curr in filename[1:]:
			if old.islower() and curr.isupper():
				outfilename += "."		
			old = curr
			outfilename += curr
		return outfilename  
	
	# remove braces from anything that isn't a checksum
	def sort_out_braces(self, filename, is_foldername):
		
		for brace in openbraces:
			
			startindex=0
			openbrace_index = filename[startindex:].find(brace)
			
			while not openbrace_index == -1:
				
				endbrace_index = filename[startindex:].find(closebraces[openbraces.index(brace)])
				if endbrace_index == -1:
					# there are no endbraces? 
					# remove the startbrace and return
					return filename[0:openbrace_index] + filename[openbrace_index:]
				
				# don't want checksums in foldernames. Preserve otherwise	
				elif is_checksum(filename[openbrace_index:endbrace_index+1]):
					
					if not is_foldername:
						# convert to square brackets + continue	
						filename = self.braces_to_squarebraces(filename, openbrace_index, endbrace_index)	
						# this will skip over the checksum
						startindex = endbrace_index+1
					else:
						# remove the checksum + continue
						filename = filename[0:openbrace_index] + "." + \
							filename[endbrace_index+1:]

						# this will skip over the checksum
						startindex = openbrace_index + 1
				else:
					# we have a pair of braces to remove
					# need to backconvert using startindex
					filename = filename[0:openbrace_index] + "." + \
							filename[openbrace_index+1:endbrace_index] + "." + \
							filename[endbrace_index+1:]
					startindex = startindex+1
				openbrace_index = filename[startindex:].find(brace)
		return filename

	def braces_to_squarebraces(self, filename, openbrace_index, endbrace_index):
		if filename[openbrace_index] in openbraces:
			filename = filename[0:openbrace_index] + "[" + filename[openbrace_index+1:]
		if filename[endbrace_index] in closebraces:
			filename = filename[0:endbrace_index] + "]" + filename[endbrace_index+1:]

		return filename


	# this isn't the global 'remove_list', it's any list of things to remove
	def remove_extra_details(self, filename_split, remove_list):
		self.debugprint('')	
		self.debugprint('Will remove any of : ' + ','.join(remove_list))
		#self.debugprint('Filename before removal: ' + ','.join(filename_split))
		fsplit = [ item for item in filename_split if not item in remove_list ]
		#self.debugprint('Filename after removal: ' + ','.join(fsplit))
		return fsplit

	def remove_empty_elements(self, filename_split):
		outfilename = []
		for i in filename_split:
			if not i == "":
				outfilename += [i]
		return outfilename
	
	# does this list contain '.mkv' or 'mkv' ?
	def is_fileext(self,item):
		return item in self.fileext_list
	
	def find_fileext(self,filename):
		f = filename.split('.')
		f.reverse()
		for i in f:
			if self.is_fileext(i):
				return i
		return ''
	
	def remove_following_text(self,filename_split,epno_index,is_foldername):
		
		# there is no epno in this filename
		if epno_index == -1:
			return filename_split

		if not is_foldername:
			epno_index += 1
		
		self.debugprint('filenamer.remove_following_text(' + str(filename_split) + ',' + str(epno_index) + ')')

		rmlist = []	
		for index,elem in enumerate(filename_split[epno_index:]):
			if not is_checksum(elem) and not self.is_fileext(elem):
				rmlist += [index+epno_index]
		
		rmlist.sort(reverse=True)
		
		for i in rmlist:
			del filename_split[i]

		return filename_split


@tracelogdecorator
def is_checksum(item):
	
	# 8-digit checksum + braces	
	if not len(item) == 10:
		return False

	if not item[0] in openbraces or not item[-1] in closebraces:
		return False	
		
	for i in item[1:9]:
		if not i in hexdigits:
			return False
	
	return True


