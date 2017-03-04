
class FullWordEpno(object):

    # TODO this is a very similar pattern to DigitsInEpno
    @tracelogdecorator
    def is_eng_number(self, substring, whole_item=''):
        if substring in self.known_eng_numbers:
            return self.known_eng_numbers[substring]

        if substring in eng_numbers:
            whole_item_text = ', from %s' % (whole_item,) if whole_item else ''
            treat_as_epno = booloptionator(
                'Is "%s"%s a part number?' % (substring, whole_item_text),
                yesno=True,
                default_false=True)
            self.known_eng_numbers[substring] = treat_as_epno
            return treat_as_epno
        return False


