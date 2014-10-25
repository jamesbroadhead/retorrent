
import os

def touch(fname):
    with open(fname, 'a'):
        os.utime(fname, None)
