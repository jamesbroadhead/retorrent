from .optionator import optionator


# TODO attrs?
class DigitsInEpnoStates(object):
    UNSET_SENTINEL = object()
    NOT_AN_EPNO_SENTINEL = object()

    TRANSIENT_STATES = {UNSET_SENTINEL, NOT_AN_EPNO_SENTINEL}


class DigitsInEpno(object):
    """
    Holds the information about the length of strings to convert into
    episode numbers. Responsible for interactively asking the user for information,
    caching their responses & responding non-interactively where appropriate
    afterwards.
    """
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
    digits_in_epno = DigitsInEpnoStates.UNSET_SENTINEL

    _noninteractive_default_value = 2

    def get_noninteractive(self):
        """ Non-interactively return the current value, or default_value if unset
        """
        if self.digits_in_epno is DigitsInEpnoStates.UNSET_SENTINEL:
            return self._noninteractive_default_value
        return self.digits_in_epno

    def get(self, split_fn, item):
        """
        Sometimes-interactively, or cached, return the number of digits for an epno
        """
        if self.digits_in_epno is DigitsInEpnoStates.UNSET_SENTINEL:
            die = self._ask_for_digits_in_epno(split_fn, item)

            if not die in DigitsInEpnoStates.TRANSIENT_STATES:
                self.digits_in_epno = die
            return die

        return self.digits_in_epno

    def _ask_for_digits_in_epno(self, split_fn, item):
        """
        Ask the user to define the number of digits in a valid episode number.
        *must* return an integer, even if an answer was not forthcoming
        """
        # TODO: this must cache specific results for the current run to avoid repeatedly asking the same question when there's a number in the title

        # TODO: circular dep here -- what ever to do??
        # => need formatter to format options
        # => formatter needs a DIE to format options
        default_value = 2
        question = 'In: "' + '.'.join(split_fn) + '", ' + item + ' means:'

        options = {
            EpnoFormatter.format(
                split_fn, item[1:3], series=item[0], digits_in_epno=2): 2,
            EpnoFormatter.format(
                split_fn, item, digits_in_epno=3): 3,
            'Should not be converted!': DigitsInEpnoStates.NOT_AN_EPNO_SENTINEL
        }

        keys = options.keys()
        keys.sort(reverse=True)

        answer = optionator(question, keys)

        if answer == '':
            print "Bad input - taking 2-digit epno"
            return default_value
        return options[answer]
