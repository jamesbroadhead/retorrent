import logging



from redecorators import tracelogdecorator

from .restring import alphabet, conv_eng_number, conv_from_alphabet, dotjoin, eng_numbers




class EpnoFormatter(object):
    """ Class to create an episode-number string from various inputs

    This class holds state to cache user responses
    """

    #pylint: disable=too-many-arguments
    @tracelogdecorator
    @classmethod
    def format(cls, split_fn, epno_raw, series_raw=None, nextitem='', digits_in_epno=None, is_movie=False, num_interesting_files=1):
        """
        Format an episode number, and optionally a series number into a standardised
        form (s01e01 or similar)

        @param epno: a raw string representing the episode number
        @param series: if set, a formatted string representing the series number
        @param digits_in_epno: integer, overrides cls._digits_in_epno
        """
        epno = cls.format_digit(split_fn, epno_raw, digits_in_epno=digits_in_epno)

        if len(nextitem) > 0 and cls.is_raw_epno(split_fn, nextitem):
            # this is a range of episodes. horrible
            epno += cls.format_digit(split_fn, nextitem, digits_in_epno=digits_in_epno)

        if series_raw is None:
            # movies don't come in series
            if is_movie:
                if num_interesting_files == 1:
                    # Only one file, getting here is a mistake
                    return ''
                return 'cd' + epno
            else:
                return 's01' + 'e' + epno

        series = cls.format_digit(split_fn, series_raw, digits_in_epno=digits_in_epno)

        if len(series) < 2:
            series = "0" + series

        return 's' + series + 'e' + epno

    def format_digit(self, split_fn, epno, digits_in_epno=None):
        """
        This formats a single field (eg, an episode number or series number.

        @param digits_in_epno: integer. If set, overrides self._digits_in_epno
        """
        if self.is_eng_number(epno):
            epno = conv_eng_number(epno)
        elif self.is_alphabetic_part_number(split_fn, epno):
            epno = conv_from_alphabet(epno)
        elif epno.isdigit():
            # cool
            pass
        else:
            if epno.lower().endswith('v2'):
                return self.format_digit(split_fn, epno[0:-2], digits_in_epno=digits_in_epno)
            elif len(epno) > 0 and epno.lower()[0] == 'e':
                return self.format_digit(split_fn, epno[1:], digits_in_epno=digits_in_epno)
            else:
                print '!!! Can\'t handle an epno like this: ', epno

        return self.pad_episode_number(epno, digits_in_epno=digits_in_epno)


    @tracelogdecorator
    def is_raw_epno(self, split_fn, epno):
        """
        This receives a number string (eg. ep01 --> True)
        It also now accepts e01 etc.

        @return boolean
        """
        if self.is_eng_number(epno) or self.is_alphabetic_part_number(split_fn,
                                                                      epno) or epno.isdigit():
            return True

        if epno.lower().endswith('v2'):
            return self.is_raw_epno(split_fn, epno[0:-2])
        elif len(epno) > 0 and epno.lower()[0] == 'e':
            return self.is_raw_epno(split_fn, epno[1:])
        return False


    # Takes a string with the epno. Makes sure that it's the right length
    # eg. diference between s01e02 and s01e002 ( or ep002)
    # ASSUME: no epno > 4 digits
    @tracelogdecorator
    def pad_episode_number(self, somestring, digits_in_epno=None):
        """
        @param digits_in_epno: integer. If set, overrides self._digits_in_epno
        """
        if digits_in_epno is None:
            die = self._digits_in_epno.get_noninteractive()
        else:
            die = digits_in_epno

        if len(somestring) < die:
            outstring = '0' * (die - len(somestring)) + somestring
        else:
            outstring = somestring

        return outstring
