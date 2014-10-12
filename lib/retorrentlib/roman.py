"""
roman.py ... some roman number parsing

This code originally from:
http://code.activestate.com/recipes/81611-roman-numerals/
Rewritten by James Broadhead
2014-10: Provably wrong in some places. I don't recommend that you use this.
Not worth the effort fixing, will remove in next commit
"""
from copy import copy

n_and_b = {'M' : 1000,
           'CM': 900,
           'D' : 500,
           'CD': 400,
           'C' : 100,
           'XC': 90,
           'L' : 50,
           'XL': 40,
           'X' : 10,
           'IX': 9,
           'V' : 5,
           'IV': 4,
           'I' : 1}
n_and_b = { unicode(k): v for k, v in n_and_b.items() }

tuples = n_and_b.items()
tuples.sort(lambda a, b: cmp(a[1], b[1]), reverse=True)

numerals         = [n for n, v in tuples if len(n) == 1]
nums_and_bigrams = [n for n, v in tuples]
values           = [v for n, v in tuples if len(n) == 1]
ints_and_bigrams = [v for n, v in tuples]

numerals_asc = copy(numerals)
numerals_asc.reverse()

# TODO: generate these from the above
roman_fives = ['D','L','V']

def could_be_roman(number,debug=False):
    """
    We're only accepting 20th Century rules for Roman Numerals.
    There's no proper standard.

    >>> could_be_roman('x')
    True

    >>> could_be_roman('ix')
    True

    >>> could_be_roman('xi')
    True

    >>> could_be_roman('xii')
    True

    >>> could_be_roman('iix')
    False

    >>> could_be_roman('divx')
    False

    >>> could_be_roman('xvid')
    False

    >>> could_be_roman('llv')
    False

    >>> could_be_roman(u'ixi')
    False
    """
    number = unicode(number.upper())

    for kindex, k in enumerate(number):
        if not k in numerals_asc:
            if debug: print 'Invalid Character!'
            return False

        if kindex > 0 and roman_to_int(k) >= roman_to_int(number[kindex-1]):
            # we have ix or similar
            # xix is ok, iix is not
            if is_roman_bigram(number[kindex-1:kindex+1]):
                if debug: print 'Bigram: ',number[kindex-1:kindex+1]

                if kindex >= 2:
                    if debug: print 'comparing %s < %s' % (number[kindex-2], number[kindex])
                    if roman_to_int(number[kindex-2]) < roman_to_int(number[kindex]):
                        if debug: print 'returning false'
                        return False
            else:
                if debug :
                    print 'number[',kindex,'] == ',k
                    print '!Bigram: ', number[kindex-1:kindex+1]
                return False

    return True

def is_roman_bigram(bigram, debug=False):
    """
    # in this context, a valid bigram is any legal pair

    >>> is_roman_bigram('xx')
    True

    >>> is_roman_bigram('vv')
    False

    >>> is_roman_bigram('ii')
    True
    """
    bigram = unicode(bigram.upper())

    # either is iv, xx but not vv
    if bigram in nums_and_bigrams:
        return True
    elif len(bigram) == 2:
        if bigram[0] == bigram[1] and not _is_roman_five(bigram[0]):
            return True
        # e.g. xi , lv
        elif n_and_b[bigram[0]] > n_and_b[bigram[1]]:
            return True

    return False

def _is_roman_five(character):
    if character.upper() in roman_fives:
        return True
    return False

def int_to_roman(input):
    if not isinstance(input, int):
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
    input = unicode(input.upper())
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
    import doctest
    doctest.testmod()
