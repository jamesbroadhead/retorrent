# returns both the item and the index
def boptionator(text, option_list):
	for option in option_list:
		if option == "":
			option_list[option_list.index(option)] = "<blank>"
	
	print text
	for index,item in enumerate(option_list):
		print "\t",index+1,"./ \t", item
	user_input = raw_input(">>")
	
	if user_input == '':
		print "Taking : ", option_list[0]
		user_input = "1"
	# We've got text that's not an entry on the list 
	if not user_input.isdigit():
		return (-1,user_input)
	elif int(user_input) > len(option_list):
		print 'Bad input!!'
		return boptionator(text, option_list)

	# get back to an index
	user_input_int = int(user_input)
	the_index = user_input_int -1
	# maybe some input checking here??
	return (the_index, option_list[the_index])

# returns the item 
def optionator(text, option_list):
	answer = boptionator(text,option_list)[1]

	if answer == "<blank>" or answer == "<cancel>" or answer == '<none>':
		answer = ""
	
	return answer

# returns the index
def ioptionator(text, option_list):
	index = boptionator(text,option_list)[0]

	return index 


# optionator, but removes duplicates
# TODO: Remove second dup, not first
# DANGER -- SORTS LIST
def eqoptionator(text, option_list):
	
	known_options = set()
	newlist = []

	for o in option_list:
		if not o in known_options:
			newlist.append(o)
			known_options.add(o)
	
	option_list[:] = newlist

	answer = optionator(text, option_list)
	
	return answer

def booloptionator(text,option_list):
	answer = optionator(text,option_list)
	
	if answer == 'True':
		return True
	elif answer == 'False':
		return False 
	else:
		return booloptionator(text,option_list)
