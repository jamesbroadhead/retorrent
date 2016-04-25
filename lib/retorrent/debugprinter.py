""" retorrent.debugprinter """
import logging


class Debugprinter(object):

    def __init__(self):
        logging.info('Initing a debugprinter')

    @staticmethod
    def debugprint(string, lists=None):
        if lists is None:
            lists = []

        logging.info(string)
        for l in lists:
            logging.info(l)
