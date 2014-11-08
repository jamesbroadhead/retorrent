""" os_utils.context_handlers """
import os

class cd(object):
    """
    http://stackoverflow.com/a/13197763
    """
    def __init__(self, newPath):
        self.savedPath = os.path.expanduser('~') # safe default
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)
