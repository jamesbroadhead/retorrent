# This code originally from: 
# http://code.activestate.com/recipes/81611-roman-numerals/
# Significantly patched by James Broadhead

numerals = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
values = [1000,500,100,50,10,5,1]

numerals_asc = numerals[:]
numerals_asc.reverse()

nums_and_bigrams = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
ints_and_bigrams = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)


n_and_b = {'M':1000,\
			'CM':900,\
			'D'	: 500,\
			'CD': 400,\
			'C' : 100,\
			'XC': 90,\
			'L' : 50,\
			'XL': 40,\
			'X' : 10,\
			'IX': 9,\
			'V' : 5,\
			'IV': 4,\
			'I' : 1}


roman_fives = ['D','L','V']

# We're only accepting 20th Century rules for Roman Numerals. 
# There's no proper standard.
def could_be_roman(number,debug=False):
	number = number.upper()
	
	for kindex,k in enumerate(number):
		if not k in numerals_asc:
			if debug: print 'Invalid Character!'	
			return False

		prev_largest = k
		
		# must catch LL etc.
		if kindex > 0 and roman_to_int(k) > roman_to_int(number[kindex-1]):

			# we have ix or similar	
			# xix is ok, iix is not
			if is_roman_bigram(number[kindex-1:kindex+1]):
				if debug: print 'Bigram: ',number[kindex-1:kindex+1] 
				if kindex >= 2:
					if roman_to_int(number[kindex-2]) < roman_to_int(number[kindex]):
						return False	
			else:
				if debug : 
					print 'number[',kindex,'] == ',k
					print '!Bigram: ', number[kindex-1:kindex+1]
				return False

	return True

# in this context, a valid bigram is any legal pair
def is_roman_bigram(bigram,debug=False):
	# either is iv, xx but not vv
	if bigram.upper() in nums_and_bigrams:
		return True 
	elif len(bigram) == 2:
		if bigram[0] == bigram[1] and not is_roman_five(bigram[0]):
			return True
		# e.g. xi , lv
		elif n_and_b[bigram[0]] > n_and_b[bigram[1]]:
			return True

	return False

def is_roman_five(character):
	if character.upper() in roman_fives:
		return True
	return False

def int_to_roman(input):
   if type(input) != type(1):
      raise TypeError, "expected integer, got %s" % type(input)
   if not 0 < input < 4000:
      raise ValueError, "Argument must be between 1 and 3999"   
   result = ""
   for i in range(len(ints_and_bigrams)):
      count = int(input / ints_and_bigrams[i])
      result += nums_and_bigrams[i] * count
      input -= ints_and_bigrams[i] * count
   return result

def roman_to_int(input):
	input = input.upper()
	places = []
	for c in input:
		if not c in numerals:
			raise ValueError, "input is not a valid roman numeral: %s" % input
	for i in range(len(input)):
		c = input[i]
		value = values[numerals.index(c)]
		# If the next place holds a larger number, this value is negative.
		try:
			nextvalue = values[numerals.index(input[i +1])]
			if nextvalue > value:
				value *= -1
		except IndexError:
			# there is no next place.
			pass
		places.append(value)
	sum = 0
	for n in places: sum += n
	# Easiest test for validity...
	if int_to_roman(sum) == input:
		return sum
	else:
		raise ValueError, 'input is not a valid roman numeral: %s' % input

if __name__ == '__main__':
	
	debug_irb = False
	debug_cbr = False

	print 'Testing: is_roman_bigram()'	
	for i in [ ('xx',True), ('vv',False), ('ii',True) ]:
		if not is_roman_bigram(i[0],debug_irb) == i[1]:
			print i[0] + '\t ==> ' + 'ERROR'
		else:
			print i[0]

	print 'Testing: could_be_roman()'
	for i in [ 	('x',True) , \
				('ix',True),\
				('xi',True),\
				('xii',True),\
				('iix',False),\
				('divx',False),\
				('xvid',False),\
				('llv',False)
		]:
		if not could_be_roman(i[0],debug_cbr) == i[1]:
			print i[0] + '\t ==> ' + 'ERROR'
		else:
			print i[0]

	print 'Tests finished'
