""" retorrent.optionator """

CANCEL = '<cancel>'


# returns both the item and the index
def boptionator(text, option_list):
    for option in option_list:
        if option == "":
            option_list[option_list.index(option)] = "<blank>"

    print text
    for index, item in enumerate(option_list):
        print "\t%s./ \t %s" % (index + 1, item)
    user_input = raw_input(">>")

    if user_input == '':
        print "Taking : ", option_list[0]
        user_input = "1"
    # We've got text that's not an entry on the list
    if not user_input.isdigit():
        return (-1, user_input)
    elif int(user_input) > len(option_list):
        print 'Bad input!!'
        return boptionator(text, option_list)

    # get back to an index
    user_input_int = int(user_input)
    the_index = user_input_int - 1
    # maybe some input checking here??
    return (the_index, option_list[the_index])


# returns the item
def optionator(text, option_list):
    answer = boptionator(text, option_list)[1]
    if answer in ['<blank>', CANCEL, '<none>']:
        return ''
    return answer


# returns the index
def ioptionator(text, option_list):
    return boptionator(text, option_list)[0]


# optionator, but removes duplicates
# TODO: Remove second dup, not first
# DANGER -- SORTS LIST
def eqoptionator(text, option_list):
    newlist = []
    for o in option_list:
        if not o in newlist:
            newlist.append(o)

    answer = optionator(text, newlist)
    return answer


def booloptionator(text, yesno=False, default_false=False):
    option_list = ['True', 'False']
    if yesno:
        option_list = ['Yes', 'No']

    if default_false:
        option_list.reverse()

    answer = optionator(text, option_list)
    answer = answer.lower()

    if answer in {'true', 'yes'}:
        return True
    elif answer in {'false', 'no'}:
        return False
    elif default_false:
        return False
    return True
