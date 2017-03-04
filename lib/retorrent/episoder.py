""" retorrent.episoder """
import logging

from os_utils.textcontrols import bold
from redecorators import tracelogdecorator

from .braced import is_year
from .digits_in_epno import DigitsInEpno, DigitsInEpnoStates
from .epno_formatter import EpnoFormatter
from .optionator import booloptionator
from .relist import replace_singleitem, replace_doubleitem
from .restring import alphabet, dotjoin, eng_numbers


class Episoder(object):
    #pylint: disable=too-many-public-methods
    identifiers = {
        'start': ['s', 'e', 'd', 'p', 'ep', 'cd', 'pt', 'part', 'side', 'series', 'episode'],
        'start_special': ['op', 'ed']
    }
    numbers_to_ignore = ['720', '264']
    pairs_to_ignore = [('5', '1'), ('8', 'bit')]  # 5.1, 8-bit

    # for folders with many files, to avoid asking multiple times
    treat_single_letters_as_epnos = None

    known_romans = {}
    known_eng_numbers = {}

    num_interesting_files = 0
    is_movie = False
    interactive = False

    def __init__(self):
        self.preserve_years = set()
        self._epno_formatter = EpnoFormatter()
            self._digits_in_epno = DigitsInEpno()

        def __repr__(self):
            return '<Episoder>'

        def set_num_interesting_files(self, num_interesting_files):
            self.num_interesting_files = num_interesting_files

        def set_movie(self, is_movie):
            """
            This exists to preserve caches of user responses, but change operation
            as new information appears.

            #future: rm this, and re-instantiate Episoder instead (or a MovieEpisoder).
            This will require encapsulating the cached user responses from the logic
            here.
            """
            self.is_movie = is_movie

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
                    if self._epno_formatter.is_raw_epno(split_fn, remainder):

                        if start_ident in self.identifiers['start']:
                            # check the next item before committing
                            if self.is_raw_serno(split_fn, item) and self._epno_formatter.is_raw_epno(split_fn,
                                                                                      nextitem):
                                split_fn = replace_doubleitem(
                                    split_fn, index,
                                    self._epno_formatter.format(split_fn, nextitem, remainder))
                                return split_fn

                            else:
                                split_fn[index] = self._epno_formatter.format(split_fn, remainder)
                                return split_fn

                        elif start_ident in self.identifiers['start_special']:
                            epno = self._epno_formatter.format_digit(split_fn, remainder)
                            split_fn[index] = subitem + epno
                            return split_fn

                        else:
                            raise Exception('Bad start_ident in loop: %r' % (start_ident,))

                    elif remainder.isalnum() and 'e' in remainder:
                        maybe_serno = remainder.split('e')[0]
                        maybe_epno = remainder.split('e')[1]
                        if self.is_raw_serno(split_fn, maybe_serno) and self._epno_formatter.is_raw_epno(split_fn,
                                                                                         maybe_epno):
                            split_fn[index] = self._epno_formatter.format(split_fn, maybe_epno,
                                                                          maybe_serno)
                            return split_fn

                # // eg. s04.e05
                elif self.is_raw_serno(split_fn, remainder) and self._epno_formatter.is_raw_epno(split_fn, nextitem):
                    if start_ident in self.identifiers['start']:
                        split_fn[index] = self._epno_formatter.format(split_fn, nextitem, remainder)
                        split_fn[index + 1] = ''
                        return split_fn

                elif len(item) == len(subitem) and self._epno_formatter.is_raw_epno(split_fn, nextitem):
                    if start_ident in self.identifiers['start']:
                        epno = self._epno_formatter.format(split_fn, nextitem)
                    else:
                        # 'start_special' -- only want a number, not a full s01e01 string
                        epno = start_ident + self._epno_formatter.format_digit(split_fn, nextitem)
                    split_fn = replace_doubleitem(split_fn, index, epno)
                    return split_fn

            logging.info('convert_if_episode_number: finished checking start_ident for %r', item)

            if item.isdigit():
                logging.info('convert_if_episode_number: checking numerals for %r', item)
                if self.is_movie:
                    # it's normal for movies to have a number in the title
                    # eg. Predator 2, etc
                    die = self._digits_in_epno.get(split_fn, item)
                    if die == DigitsInEpnoStates.NOT_AN_EPNO_SENTINEL:
                    # the user indicated that the item wasn't an epno
                    return None

            # eg. 1  or 2
            if len(item) == 1:
                # 1.01 => s01e01
                if self._epno_formatter.is_raw_epno(split_fn, nextitem):
                    split_fn = replace_doubleitem(
                        split_fn, index, self._epno_formatter.format(split_fn, nextitem, item))
                else:  # 1 => s01e01
                    split_fn[index] = self._epno_formatter.format(split_fn, item)
                return split_fn

            # eg. 45
            elif len(item) == 2:
                if self._epno_formatter.is_raw_epno(split_fn, nextitem):
                    return replace_doubleitem(split_fn, index,
                                              self._epno_formatter.format(split_fn, nextitem, item))
                else:
                    return replace_singleitem(split_fn, index,
                                              self._epno_formatter.format(split_fn, item))
            # eg. 302 -> may be episode 302, or s03e02
            elif len(item) == 3:
                die = self._digits_in_epno.get(split_fn, item)
                if die == DigitsInEpnoStates.NOT_AN_EPNO_SENTINEL:
                    # the user indicated that the item wasn't an epno
                    return None
                elif die == 2:
                    split_fn[index] = self._epno_formatter.format(split_fn, item[1:], item[0])
                elif die == 3:
                    split_fn[index] = self._epno_formatter.format(split_fn, item)
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
                    split_fn[index] = self._epno_formatter.format(split_fn, item[2:], item[0:2])
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
            if (self._epno_formatter.is_raw_epno(split_fn, item.split('of')[0]) and
                    self._epno_formatter.is_raw_epno(split_fn, item.split('of')[1])):
                split_fn[index] = self._epno_formatter.format(split_fn, item.split('of')[0])
                return split_fn

        # just a number - treat as the episode number of season 1
        elif self._epno_formatter.is_raw_epno(split_fn, item):
            split_fn[index] = self._epno_formatter.format(split_fn, item)
            return split_fn

        logging.info('convert_if_episode_number: default fallthrough on %r', item)

        return None

    @tracelogdecorator
    def convert_number_divider_number(self, split_fn, item):
        """ <variable-length-number> + <divider symbol> + <variable_length_number> """
        if not len(item) >= 3:
            return

        for i in range(1, len(item)):
            subitem = item[0:i]
            divider = item[i]
            supitem = item[i + 1:]
            if subitem.isdigit() and divider.isalpha() and supitem.isdigit():
                # special-case divider=='v' as a version (not an episode-indicator)
                # eg. 1v1, 02v2 -> s01e01, s01e02
                if divider == 'v':
                    return self._epno_formatter.format(split_fn, subitem)
                item = self._epno_formatter.format(split_fn, supitem, subitem)
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

    @staticmethod
    def nextitem_if_exists(split_fn, currindex):
        if len(split_fn) > currindex + 1:
            nextitem = split_fn[currindex + 1]
            return nextitem
        return ''

    def is_raw_serno(self, split_fn, serno):
        if len(serno) > 0 and serno.lower().startswith('s'):
            return self._epno_formatter.is_raw_epno(split_fn, serno[1:])
        elif len(serno) > 0 and serno.lower().startswith('e'):
            return False

        return self._epno_formatter.is_raw_epno(split_fn, serno)



    def format_epno(self, *args, **kwargs):
        return self._epno_formatter.format(*args, is_movie=self.is_movie, num_interesting_files=self.num_interesting_files, **kwargs)
