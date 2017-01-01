""" retorrent.episoder """
import logging

from os_utils.textcontrols import bold
from redecorators import tracelogdecorator

from .braced import is_year
from .optionator import booloptionator, optionator
from .relist import replace_singleitem, replace_doubleitem
from .restring import alphabet, conv_eng_number, conv_from_alphabet, dotjoin, eng_numbers

# TODO: Find all assumptions about two-digit episode numbers + mark with ASSUME
# TODO: Fix all ASSUMES about 2-digit epnummbers


class Episoder(object):
    #pylint: disable=too-many-public-methods
    identifiers = {'start': ['s', 'e', 'd', 'p', 'ep', 'cd', 'pt', 'part', 'side', 'series',
                             'episode'],
                   'start_special': ['op', 'ed']}
    numbers_to_ignore = ['720', '264']
    pairs_to_ignore = [('5', '1')]  # 5.1

    UNSET_SENTINEL = object()
    NOT_AN_EPNO_SENTINEL = object()

    # for the current item, the number of digits we expect in the episode number.
    # this serves a number of purposes:
    # in parsing:
    #   used to determine if a string is a valid epno
    #   may be set to NOT_AN_EPNO_SENTINEL if the user was posed the question
    # in generation:
    #   used to format the output string
    #
    # Valid values: (integers), UNSET_SENTINEL, NOT_AN_EPNO_SENTINEL
    #
    # #future: this should be refactored away to be single-use
    digits_in_epno = UNSET_SENTINEL

    # for folders with many files, to avoid asking multiple times
    treat_single_letters_as_epnos = None

    known_romans = {}
    known_eng_numbers = {}

    num_interesting_files = 0
    is_movie = False
    interactive = False

    def __init__(self):
        self.preserve_years = set()

    def __repr__(self):
        return '<Episoder>'

    @staticmethod
    def booloptionator(question, yesno=True, default_false=True):
        return booloptionator(question, yesno=yesno, default_false=default_false)

    @staticmethod
    def optionator(question, keys):
        return optionator(question, keys)

    def set_num_interesting_files(self, num_interesting_files):
        self.num_interesting_files = num_interesting_files

    def set_movie(self, is_movie):
        self.is_movie = is_movie

    # TODO: need to sort out dirs that have 01-04 or similar
    # TODO: new episode numbering "episode 1", [01x01]
    @tracelogdecorator
    def add_series_episode_details(self, split_fn):
        for index, item in enumerate(split_fn):
            nextitem = self.nextitem_if_exists(split_fn, index)

            if item in self.numbers_to_ignore or (item, nextitem) in self.pairs_to_ignore:
                continue

            result = self.convert_if_episode_number(split_fn, index)
            if result:
                return result, index

        return split_fn, -1

    @tracelogdecorator
    def convert_if_episode_number(self, split_fn, index):
        """
        Return a copy of split_fn with episode details converted to a canonical form

        WARNING: may mutate the input.

        @return split_filename: if an episode number was detected, return a copy of
            split_filename with the episode details in canonical form. If no details were
            detected, return None
        """
        #pylint: disable=too-many-branches,too-many-return-statements,too-many-statements
        item = split_fn[index]
        nextitem = self.nextitem_if_exists(split_fn, index)

        # eg. part, episode
        for start_ident in self.identifiers['start'] + self.identifiers['start_special']:
            logging.info('convert_if_episode_number: checking start_ident=%r', start_ident)
            subitem = item[0:len(start_ident)]
            remainder = item[len(subitem):]

            if not subitem == start_ident:
                continue

            elif len(item) > len(start_ident):
                if self.is_raw_epno(split_fn, remainder):

                    if start_ident in self.identifiers['start']:
                        # check the next item before committing
                        if self.is_raw_serno(split_fn, item) and self.is_raw_epno(split_fn,
                                                                                  nextitem):
                            split_fn = replace_doubleitem(
                                split_fn, index,
                                self.gen_full_epno_string(split_fn, nextitem, remainder))
                            return split_fn

                        else:
                            split_fn[index] = self.gen_full_epno_string(split_fn, remainder)
                            return split_fn

                    elif start_ident in self.identifiers['start_special']:
                        epno = self.nice_epno_from_raw(split_fn, remainder)
                        split_fn[index] = subitem + epno
                        return split_fn

                    else:
                        raise Exception('Bad start_ident in loop: %r' % (start_ident,))

                elif remainder.isalnum() and 'e' in remainder:
                    maybe_serno = remainder.split('e')[0]
                    maybe_epno = remainder.split('e')[1]
                    if self.is_raw_serno(split_fn, maybe_serno) and self.is_raw_epno(split_fn,
                                                                                     maybe_epno):
                        split_fn[index] = self.gen_full_epno_string(split_fn, maybe_epno,
                                                                    maybe_serno)
                        return split_fn

            # // eg. s04.e05
            elif self.is_raw_serno(split_fn, remainder) and self.is_raw_epno(split_fn, nextitem):
                if start_ident in self.identifiers['start']:
                    split_fn[index] = self.gen_full_epno_string(split_fn, nextitem, remainder)
                    split_fn[index + 1] = ''
                    return split_fn

            elif len(item) == len(subitem) and self.is_raw_epno(split_fn, nextitem):
                if start_ident in self.identifiers['start']:
                    epno = self.gen_full_epno_string(split_fn, nextitem)
                else:
                    # 'start_special' -- only want a number, not a full s01e01 string
                    epno = start_ident + self.nice_epno_from_raw(split_fn, nextitem)
                split_fn = replace_doubleitem(split_fn, index, epno)
                return split_fn

        logging.info('convert_if_episode_number: finished checking start_ident for %r', item)

        if item.isdigit():
            logging.info('convert_if_episode_number: checking numerals for %r', item)
            # eg. 1  or 2
            if len(item) == 1:
                # 1.01 => s01e01
                if self.is_raw_epno(split_fn, nextitem):
                    split_fn = replace_doubleitem(
                        split_fn, index, self.gen_full_epno_string(split_fn, nextitem, item))
                else:  # 1 => s01e01
                    split_fn[index] = self.gen_full_epno_string(split_fn, item)
                return split_fn

            # eg. 45
            elif len(item) == 2:
                if self.is_raw_epno(split_fn, nextitem):
                    return replace_doubleitem(split_fn, index,
                                              self.gen_full_epno_string(split_fn, nextitem, item))
                else:
                    return replace_singleitem(split_fn, index, self.gen_full_epno_string(split_fn,
                                                                                         item))
            # eg. 302 -> may be episode 302, or s03e02
            elif len(item) == 3:
                die = self.get_digits_in_epno(split_fn, item)
                if die == self.NOT_AN_EPNO_SENTINEL:
                    # the user indicated that the item wasn't an epno
                    return None
                elif die == 2:
                    split_fn[index] = self.gen_full_epno_string(split_fn, item[1:], item[0])
                elif die == 3:
                    split_fn[index] = self.gen_full_epno_string(split_fn, item)
                else:
                    raise Exception('ERROR! Messed up around digits_in_epno')

                return split_fn

            # eg. 0104 == s01e04
            elif len(item) == 4:
                # de-unicode so that memoize works
                if is_year(str(item), interactive=self.interactive):
                    # it is a year, preserve it
                    return None
                else:
                    split_fn[index] = self.gen_full_epno_string(split_fn, item[2:], item[0:2])
                    return split_fn

            # it's a >5 digit number ... boring
            return None

        logging.info('convert_if_episode_number: finished checking numerals for %r', item)

        # 1x1 / 1x02 / 1x001 / 1e3
        ndn = self.convert_number_divider_number(split_fn, item)
        if ndn is not None:
            return replace_singleitem(split_fn, index, ndn)

        # Special case: "pilot"
        if len(item) == 5 and item == "pilot":
            split_fn[index] = "s00e00"
            return split_fn

        # Special case: 1of5, 01of05
        elif 'of' in item:
            if (self.is_raw_epno(split_fn, item.split('of')[0]) and
                    self.is_raw_epno(split_fn, item.split('of')[1])):
                split_fn[index] = self.gen_full_epno_string(split_fn, item.split('of')[0])
                return split_fn

        # just a number - treat as the episode number of season 1
        elif self.is_raw_epno(split_fn, item):
            split_fn[index] = self.gen_full_epno_string(split_fn, item)
            return split_fn

        logging.info('convert_if_episode_number: default fallthrough on %r', item)

        return None

    @tracelogdecorator
    def gen_full_epno_string(self, split_fn, epno_raw, series_raw=None, nextitem=''):
        """
        @param epno: a raw string representing the episode number
        @param series: if set, a formatted string representing the series number
        """
        epno = self.nice_epno_from_raw(split_fn, epno_raw)

        if len(nextitem) > 0 and self.is_raw_epno(split_fn, nextitem):
            # this is a range of episodes. horrible
            epno += self.nice_epno_from_raw(split_fn, nextitem)

        if series_raw is None:
            # movies don't come in series
            if self.is_movie and self.num_interesting_files == 1:
                # Only one file, getting here is a mistake
                return ''
            elif self.is_movie:
                # TODO: verify that epno is single-digit only :(
                return 'cd' + epno
            else:
                return 's01' + 'e' + epno

        series = self.nice_epno_from_raw(split_fn, series_raw)

        if len(series) < 2:
            series = "0" + series

        return 's' + series + 'e' + epno

    @tracelogdecorator
    def convert_number_divider_number(self, split_fn, item):
        """ <variable-length-number> + <divider symbol> + <variable_length_number> """
        if not len(item) >= 3:
            return

        # TODO: REEEEEGEX
        for i in range(1, len(item)):
            subitem = item[0:i]
            divider = item[i]
            supitem = item[i + 1:]
            if subitem.isdigit() and divider.isalpha() and supitem.isdigit():
                # special-case divider=='v' as a version (not an episode-indicator)
                # eg. 1v1, 02v2 -> s01e01, s01e02
                if divider == 'v':
                    return self.gen_full_epno_string(split_fn, subitem)
                item = self.gen_full_epno_string(split_fn, supitem, subitem)
                return item
        return None

    def get_good_epno(self, filename):
        return self.get_good_epno_from_split(filename.split('.'))

    def get_good_epno_from_split(self, filename_split):
        for i in filename_split:
            if self.is_good_epno(i):
                return i

        return ''

    @classmethod
    @tracelogdecorator
    def is_good_epno(cls, item):
        if len(item) >= 4:
            if item[0:2] == 'cd' and item[2:].isdigit():
                return True
            elif item[0] == 's' and item[1:3].isdigit() and \
                    item[3] == 'e' and item[4:].isdigit():
                return True
            elif item[0:2] in cls.identifiers['start_special'] and item[2:].isdigit():
                return True
        return False

    def gen_n_digit_epno(self, split_fn, N, epno, series='', nextitem=''):
        #pylint: disable=too-many-arguments
        tmp = self.digits_in_epno
        self.digits_in_epno = N
        output = self.gen_full_epno_string(split_fn, epno, series, nextitem)
        self.digits_in_epno = tmp
        return output

    def get_digits_in_epno(self, split_fn, item):
        if self.digits_in_epno is self.UNSET_SENTINEL:
            self.digits_in_epno = self.ask_for_digits_in_epno(split_fn, item)
        return self.digits_in_epno

    def ask_for_digits_in_epno(self, split_fn, item):
        """
        Ask the user to define the number of digits in a valid episode number.
        *must* return an integer, even if an answer was not forthcoming
        """
        default_value = 2
        question = 'In: "' + '.'.join(split_fn) + '", ' + item + ' means:'

        options = {self.gen_n_digit_epno(split_fn, 2, item[1:3], item[0]): 2,
                   self.gen_n_digit_epno(split_fn, 3, item): 3,
                   'Not an episode number!': self.NOT_AN_EPNO_SENTINEL}

        keys = options.keys()
        keys.sort(reverse=True)

        answer = self.optionator(question, keys)

        if answer == '':
            print "Bad input - taking 2-digit epno"
            return default_value
        return options[answer]

    @staticmethod
    def nextitem_if_exists(split_fn, currindex):
        if len(split_fn) > currindex + 1:
            nextitem = split_fn[currindex + 1]
            return nextitem
        return ''

    def is_raw_serno(self, split_fn, serno):
        if len(serno) > 0 and serno.lower().startswith('s'):
            return self.is_raw_epno(split_fn, serno[1:])
        elif len(serno) > 0 and serno.lower().startswith('e'):
            return False

        return self.is_raw_epno(split_fn, serno)

    @tracelogdecorator
    def is_raw_epno(self, split_fn, epno):
        """
        This receives a number string (eg. ep01 --> 01)
        It also now accepts e01 etc.
        """
        if self.is_eng_number(epno) or self.is_alphabetic_part_number(split_fn,
                                                                      epno) or epno.isdigit():
            return True

        if epno.lower().endswith('v2'):
            return self.is_raw_epno(split_fn, epno[0:-2])
        elif len(epno) > 0 and epno.lower()[0] == 'e':
            return self.is_raw_epno(split_fn, epno[1:])
        return False

    def nice_epno_from_raw(self, split_fn, epno):
        if self.is_eng_number(epno):
            epno = conv_eng_number(epno)
        elif self.is_alphabetic_part_number(split_fn, epno):
            epno = conv_from_alphabet(epno)
        elif epno.isdigit():
            # cool
            pass
        else:
            if epno.lower().endswith('v2'):
                return self.nice_epno_from_raw(split_fn, epno[0:-2])
            elif len(epno) > 0 and epno.lower()[0] == 'e':
                return self.nice_epno_from_raw(split_fn, epno[1:])
            else:
                print '!!! Can\'t handle an epno like this: ', epno

        return self.pad_episode_number(epno)

    # Takes a string with the epno. Makes sure that it's the right length
    # eg. diference between s01e02 and s01e002 ( or ep002)
    # ASSUME: no epno > 4 digits
    def pad_episode_number(self, somestring):
        die = self.digits_in_epno
        if die == self.UNSET_SENTINEL:
            die = 0

        min_length = 2

        if die < min_length:
            die = min_length

        if len(somestring) < die:
            outstring = '0' * (die - len(somestring)) + somestring
        else:
            outstring = somestring

        return outstring

    @tracelogdecorator
    def is_alphabetic_part_number(self, split_fn, item):
        """
        @param item: string

        @return boolean: if the item was a single alphabetic character which should be treated
            as a part number
        """
        if not len(item) == 1 or not item in alphabet:
            return False

        if self.treat_single_letters_as_epnos is not None:
            logging.info(
                'is_alphabetic_part_number: skipping check, already have a default answer of: %r',
                self.treat_single_letters_as_epnos)

            return self.treat_single_letters_as_epnos

        if self.is_movie and self.num_interesting_files == 1:
            return False

        if not self.interactive:
            # We're probably dealing with torrentfiles - no ep numbers usually(?)
            # TODO [later] We definitely need episode numbers.
            return False

        return self.ask_if_single_letter_is_epno(split_fn, item)

    def ask_if_single_letter_is_epno(self, split_fn, letter):
        # nice defaults
        default_false = False
        if not (letter == 'a' or letter == 'b'):
            default_false = True

        answer = self.booloptionator('In: {}\nIs {} an episode or part number?'.format(
            bold(dotjoin(*split_fn)), bold(letter)),
                                     yesno=True,
                                     default_false=default_false)
        self.treat_single_letters_as_epnos = answer

        logging.info('%s is %s an episode number', letter, '' if answer else 'not')
        return answer

    @tracelogdecorator
    def is_eng_number(self, substring, whole_item=''):
        if substring in self.known_eng_numbers:
            return self.known_eng_numbers[substring]

        if substring in eng_numbers:
            whole_item_text = ', from %s' % (whole_item,) if whole_item else ''
            treat_as_epno = self.booloptionator('Is "%s"%s a part number?' % (substring,
                                                                              whole_item_text),
                                                yesno=True,
                                                default_false=True)
            self.known_eng_numbers[substring] = treat_as_epno
            return treat_as_epno
        return False
