import datetime
import roman


from debugprinter import debugprinter
from optionator import *
from textcontrols import *


# TODO: Find all assumptions about two-digit episode numbers + mark with ASSUME
# TODO: Fix all ASSUMES about 2-digit epnummbers

class episoder:
	
	alphabet = "abcdefghijklmnopqrstuvwxyz"
	eng_numbers = ['one','two','three','four','five','six','seven','eight','nine','ten']
	
	identifiers = {	1: ['e', 'd','p'], \
					2: ["ep", "cd", "pt" ], \
					4: ['part', 'side'],	\
					7: ['episode']
	}
	special_cases = { 2: ['op', 'ed'] }	
	
	resolutions = [ '720' ]

	identifiers_keys = identifiers.keys()
	identifiers_keys.sort(reverse=True)
	special_cases_keys = special_cases.keys()
	special_cases_keys.sort(reverse=True)

	digits_in_epno = 0
	single_letter_is_epno = -1

	num_interesting_files = 0
	is_movie = False
	interactive = False	
	def __init__(self,debugprinter=debugprinter(False)):
		self.debugprinter = debugprinter
		self.known_years = range(1980,2015)

	def debugprint(self, str, listol=[]):
		self.debugprinter.debugprint(str,listol)	
		
		
	# TODO: need to sort out dirs that have 01-04 or similar
	# TODO: new episode numbering "episode 1", [01x01]
	# TODO: Rewrite this to incorporate is_raw_episode_details	
	def add_series_episode_details(self, split_fn):
		for index,item in enumerate(split_fn):
			split_fn, is_epno = self.convert_if_episode_number(split_fn, index)
			
			# Only one episode number per file? 
			if is_epno:
				return split_fn,index

		return split_fn,-1
	

	def convert_if_episode_number(self, split_fn, index):
		self.debugprint('episoder.convert_if_episode_number(index=' + str(index),[['split_fn',split_fn]])
		item = split_fn[index]	
		next = self.set_next_if_exists(split_fn, index)	
		
		# eg. part, episode	
		for length in self.identifiers_keys:

			if len(item) >= length and item[0:length] in self.identifiers[length]:
				# have we caught the start of a word, or an epno
				if len(item) > length and self.is_raw_epno(item[length:]):	
					split_fn[index] = self.gen_epno(item[length:],next=next)
					return split_fn, True

				# we know that len(item) == length
				elif self.is_raw_epno(next):
					split_fn = self.replace_doubleitem(split_fn, index, \
							self.gen_epno(next))
					return split_fn, True
				else:
					# fall through
					pass

		for length in self.special_cases_keys:

			if len(item) >= length and item[0:length] in self.identifiers[length]:
				if len(item) > length:
					split_fn = self.replace_doubleitem(split_fn,index, \
							item[0:length] + nice_epno_from_raw(item[length:]))
					return split_fn, True
				elif self.is_raw_epno(next):
					split_fn[index] = item[0:2] + nice_epno_from_raw(item[length:])
					return split_fn, True
				else:
					# fall through
					pass

		if item.isdigit() and item not in self.resolutions:
			# eg. 1  or 2
			if len(item) == 1:
				#1\\01	
				if self.is_raw_epno(next):
					split_fn = self.replace_doubleitem(split_fn, index, self.gen_epno(next,item))
				else: 
					split_fn[index] = self.gen_epno(item)	
					return split_fn, True	
			# eg. 45
			elif len(item) == 2:
				split_fn[index] = self.gen_epno(item)	
				return split_fn, True	
			
			# eg. 302 
			elif len(item) == 3:
				die = self.get_digits_in_epno(split_fn,item)
				if die == 0:
					# the user indicated that the item wasn't an epno
					return split_fn, False	
				if die == 2:
					split_fn[index] = self.gen_epno(item[1:], item[0])
				elif die == 3: 
					split_fn[index] = self.gen_epno(item)
				else:
					print 'ERROR! (episoder)'
					return split_fn, False

				return split_fn, True	
			
			# eg. 0104 == s01e04
			elif len(item) == 4:
				if not self.ask_is_year(item):	
					split_fn[index] = self.gen_epno(item[2:], item[0:2])	
					return split_fn, True
				else:
					# it is a year
					return split_fn, False
			else:
				# it's a >5 digit number ... boring	
				return split_fn, False
		
		# 1x1 1x02 or  or 1x001
		elif len(item) > 3 and 'x' in item and \
				item.split('x')[0].isdigit() and item.split('x')[1].isdigit():
			split_fn[index] = self.gen_epno(item.split('x')[1], item.split('x')[0])
			return split_fn, True

		# s1e3 
		elif len(item) == 4 and item[0] == "s" and item[2] == "e" and item[1].isdigit() and item[3].isdigit():
			split_fn[index] = self.gen_epno(item[3], item[1])		
			return split_fn, True
		
		# s01e03 (awesome!)
		elif len(item) == 6 and item[0] == "s" and item[3] == "e" and item[1:3].isdigit() and item[4:6].isdigit():
			split_fn[index] = self.gen_epno(item[4:6], item[1:3])		
			return split_fn, True	
				
		# catch "pilot"	
		elif len(item) == 5 and item == "pilot":
			split_fn[index] == "s00e00"
			return split_fn, True
		
		# eg. 1of5, 01of05
		elif 'of' in item:
			if self.is_raw_epno(item.split('of')[0]) and self.is_raw_epno(item.split('of')[1]):
				split_fn[index] = self.gen_epno(item.split('of')[0])
				return split_fn, True
	
		elif self.is_raw_epno(item):
			split_fn[index] = self.gen_epno(item)
			return split_fn, True
		
		# special case - only the series number is given (eg. in folder names)
		elif len(item) > 1 and item[0] == 's' and item[1:].isdigit():
			# it's just the series number, return True but ''
			return split_fn,True
		return split_fn, False

	# TODO: How many digits in series / epno length?
	def gen_epno(self,epno,series="", next=''):
		self.debugprint('episoder.gen_epno(epno=' + str(epno) + ', series=' + str(series) + ', next=' +  next + ')')		
		
		epno = self.nice_epno_from_raw(epno)
	
		if len(next) > 0 and self.is_raw_epno(next):
			# this is a range of episodes. horrible
			epno += self.nice_epno_from_raw(next)


		if not series == "":
			if len(series) < 2:
				series = "0" + series
			
			return 's' + series + 'e' + epno
		else:
			# movies don't come in series
			if self.is_movie and self.num_interesting_files == 1:
				# Only one file, getting here is a mistake	
				return ''
			elif self.is_movie:
				return 'cd' + epno
			else:
				return 's01' + 'e' + epno
	
	def get_good_epno(self,filename):
		return self.get_good_epno_from_split(filename.split('.'))

	def get_good_epno_from_split(self,filename_split):
		for i in filename_split:
			if self.is_good_epno(i):
				return i

		return ''
	
	def is_good_epno(self,item):
		self.debugprint('episoder.is_good_epno(' + item + ')')
		if len(item) >= 4:
			if item[0:2] == 'cd' and item[2:].isdigit():
				return True
			elif item[0] == 's' and item[1:3].isdigit() and \
					item[3] == 'e' and item[4:].isdigit():
				return True

		return False
	def gen_n_digit_epno(self, N, epno,series="", next=''):
		tmp = self.digits_in_epno	
		self.digits_in_epno = N
		output = self.gen_epno(epno,series,next)
		self.digits_in_epno = tmp
		return output 

	def get_digits_in_epno(self, split_fn, item):
		if self.unknown_digits_in_epno():
			self.ask_for_digits_in_epno(split_fn,item)
		return self.digits_in_epno

	def unknown_digits_in_epno(self):
		if self.digits_in_epno == 0:
			return True
		else:
			return False 

	def ask_for_digits_in_epno(self, split_fn, item):


		question = 'In: "' + '.'.join(split_fn) + '", ' + item + ' means:'
		
		options = { \
				self.gen_n_digit_epno(2,item[1:3], item[0]) : 2, \
				self.gen_n_digit_epno(3,item) 				: 3, \
				'Not an episode number!' : 0}
		
		keys = options.keys()
		keys.sort(reverse=True)

		answer = optionator(question, keys)
		
		if answer == '':
			print "Bad input - taking 2-digit epno"
			self.digits_in_epno = 2
		else:
			self.digits_in_epno = options[answer]
	
		return
	
	def is_single_letter_is_epno_set(self):
		if self.single_letter_is_epno == -1:
			return False
		else:
			return True

	def ask_if_single_letter_is_epno(self,letter):
		
		if not self.interactive:
			# We're probably dealing with torrentfiles - no ep numbers usually(?)
			# We definitely need episode numbers. TODO
			return False

		question = 'Is ' + boldtext + letter + resetbold + ' an episode or part number?'
		
		# nice defaults
		if letter == 'a' or letter == 'b':
			options = [ 'True', 'False' ]
		else:
			options = ['False', 'True']
		
		if booloptionator(question, options):
			self.single_letter_is_epno = 1
		else:
			self.single_letter_is_epno = 0
		


	def set_next_if_exists(self, split_fn, currindex):
		if len(split_fn) > currindex + 1:
			next = split_fn[currindex+1]
			return next
		return '' 
	
	# This receives a number string (eg. ep01 --> 01)	
	def is_raw_epno(self,epno):
		if self.is_eng_number(epno) 			\
				or self.is_in_alphabet(epno)	\
				or self.is_roman_numeral(epno) 	\
				or epno.isdigit():
			return True
		else:
			if epno.lower().endswith('v2'):
				return self.is_raw_epno(epno[0:-2])
			
			return False
	
	def nice_epno_from_raw(self,epno):
		if self.is_eng_number(epno):
			epno = self.conv_eng_number(epno)
		elif self.is_roman_numeral(epno):
			epno = self.conv_from_roman(epno)
		elif self.is_in_alphabet(epno):
			epno = self.conv_from_alphabet(epno)
		elif epno.isdigit():
			# cool
			pass
		else:
			if epno.lower().endswith('v2'):
				return self.nice_epno_from_raw(epno[0:-2])
			else:	
				print '!!! Can\'t handle an epno like this: ', epno
		
		return self.pad_episode_number(epno)

	# Takes a string with the epno. Makes sure that it's the right length
	# eg. diference between s01e02 and s01e002 ( or ep002)
	# ASSUME: no epno > 4 digits
	def pad_episode_number(self, somestring):
		
		die = self.digits_in_epno 
		
		min_length = 2
		
		if die < min_length:
			die = min_length
		
		if len(somestring) < die:
			outstring = '0'*(die-len(somestring)) + somestring
		else:
			outstring = somestring
		
		return outstring 
	
	# If: 	Is a single letter
	# AND: 	Single Letters are epnos
	def is_in_alphabet(self,string):
		self.debugprint('episoder.is_in_alphabet:'+ string)
		
		if not len(string) == 1 or not string.isalpha():
			return False

		if not self.is_single_letter_is_epno_set():
			self.ask_if_single_letter_is_epno(string)
		
		# It's a single letter, and we're accepting those
		return self.single_letter_is_epno
			

	def is_roman_numeral(self, string):
		if len(string) == 0:
			return False
		if roman.could_be_roman(string):
			# testing shows that high numbers are probably just letters
			if roman.roman_to_int(string) > 30:
				return False
			return True
		return False

	def conv_from_alphabet(self, letter):
		ordinal = self.alphabet.index(letter) + 1
		return str(ordinal)
		
	def conv_from_roman(self, string):
		return str(roman.roman_to_int(string))

	def replace_doubleitem(self, split_fn, index, new_string):
		split_fn[index] = new_string
		del split_fn[index+1]
		return split_fn
	def print_partialmatch_errmsg(self,string):
		print 'Partial match; write more cases! // ', string
		return

	def is_eng_number(self,somestring):
		if somestring in self.eng_numbers:
			return True
		else:
			return False 

	def conv_eng_number(self, somestring):
		ordinal = self.eng_numbers.index(somestring) + 1
		return str(ordinal)


	def letter_to_number(self, letter):
		alphabet = "abcdefghijklmnopqrstuvwxyz"
		the_index = alphabet.index(letter)

		return the_index + 1
	
	def number_is_episodenumber(self,split_fn,index):
		print "episoder.number_is_episodenumber: assuming 2-digit is epno"
		return True
	
	def ask_is_year(self,item):
		if item.isdigit() and int(item) in self.known_years:
			return True
		elif not self.interactive:
			return False
		else:
			thisyear = datetime.datetime.now().year
			if item.isdigit() and len(item) == 4 and int(item) <= thisyear:
				is_year = booloptionator('Does ' + item + ' represent a year?', \
						['True', 'False'])
				
				if is_year: 
					self.known_years += [ item ]
					return True
		return False

	# This receives a full part of the foldername ( eg. ep01)	
	def is_raw_episode_numbering_string(self,string):	
		return self.convert_if_episode_number([string], 0)[1]
	
	def set_num_interesting_files(self,num_interesting_files):
		self.num_interesting_files = num_interesting_files

	def set_movie(self,is_movie):
		self.is_movie = is_movie
