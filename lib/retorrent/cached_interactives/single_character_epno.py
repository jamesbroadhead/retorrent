
class SingleCharacterEpno(object)
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
            return False

        return self.ask_if_single_letter_is_epno(split_fn, item)

    # TODO this is a very similar pattern to DigitsInEpno
    def ask_if_single_letter_is_epno(self, split_fn, letter):
        # nice defaults
        default_false = False
        if not (letter == 'a' or letter == 'b'):
            default_false = True

        answer = booloptionator(
            'In: {}\nIs {} an episode or part number?'.format(
                bold(dotjoin(*split_fn)), bold(letter)),
            yesno=True,
            default_false=default_false)
        self.treat_single_letters_as_epnos = answer

        logging.info('%s is %s an episode number', letter, '' if answer else 'not')
        return answer


