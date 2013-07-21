import logging

class debugprinter:

    def __init__(self, debug):
        self.debug = debug
        logging.info('Initing a debugprinter')

    def debugprint(self, string, lists=[]):
        logging.info(string)

        for l in lists:
            logging.info(l)
