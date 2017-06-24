""" os_utils.os_utils

Monolithic module containing most of this package's functionality.
"""

import ctypes
import errno
import platform
import os
from os.path import abspath, basename, dirname, expanduser, realpath
from os.path import exists as pexists
from os.path import join as pjoin

from redecorators.tracelogdecorator import tracelogdecorator


def freespace(path, si_prefix=''):
    """
    Returns the number of free bytes on the drive that ``p`` is on

    I use the f_bavail attribute instead of f_bfree, since the latter
        includes blocks that are reserved for the the super-user.s use.
        I'm not sure, however, on the distinction between f_bsize and f_frsize.

    From: http://atlee.ca/blog/2008/02/23/getting-free-diskspace-in-python/
    """

    # http://stackoverflow.com/questions/51658/cross-platform-space-remaining-on-volume-using-python
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(path), None, None, ctypes.pointer(free_bytes))
        space = free_bytes.value
    else:
        s = os.statvfs(path)

        # MacOS compat;
        #     f_bsize is the preferred block size while .f_frsize is the
        #    fundamental block size

        space = s.f_frsize * s.f_bavail

    if si_prefix:
        SI_pos = ['k', 'M', 'G', 'T']
        if not si_prefix in SI_pos:
            raise ValueError('Invalid SI prefix')
        divisor = 1024 * SI_pos.index(si_prefix)
        space = float(space) / divisor

    return space


@tracelogdecorator
def enough_space(orig_paths, proposed_path):
    proposed_path = expanduser(proposed_path)
    # first check if they're on the same volume
    if same_volume(orig_paths, proposed_path):
        return True

    proposed_path = expanduser(proposed_path)

    filesize_B = sum([os.path.getsize(orig_path) for orig_path in orig_paths])
    if not pexists(proposed_path):
        proposed_path = dirname(proposed_path.rstrip('/'))

    if filesize_B < freespace(proposed_path):
        return True
    return False


@tracelogdecorator
def same_volume(orig_paths, proposed_path):
    pp = proposed_path

    # Should only be one loop
    #    (eg. video/tv/foo -> video/tv)
    while not pexists(pp):
        pp = dirname(pp)
    prop_dev = device_number(pp)

    for p in orig_paths:
        if not prop_dev == device_number(p):
            return False
    return True


@tracelogdecorator
def device_number(path):
    return os.stat(expanduser(path)).st_dev


def hostname():
    """ get the hostname without using the network stack """
    return os.uname()[1]


def mkdir_p(path):
    """
    Replicate functionality of mkdir -p
    from http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
    """

    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            # some error other than dir already exists
            raise


def get_foldername(path):
    """
    @param path: a string, which should be a path
    """
    if not path:
        return ''

    return basename(path.strip('/'))


def str2utf8(string):
    if isinstance(string, str):
        u = string
    else:
        u = str(string, 'utf-8', errors='ignore')
    return u


def diskspace_used(path, si='kiB'):

    filestat = os.stat(path)
    disk_filesize_b = filestat.st_blocks * filestat.st_blksize

    if si == 'kiB':
        return disk_filesize_b / (8 * 1024)
    elif si == 'B':
        return disk_filesize_b / (8)
    # kiB
    return disk_filesize_b / (8 * 1024)


def sym_sametarget(a, b):
    return realpath(a) == realpath(b)


def smbify(path):
    """
    For a given unix path, return a version that is legal for samba
    """
    path = path.replace(':', '_')
    path = path.replace(';', '_')

    return path


def myglob(arg):
    """
    with cd(dirname(partial_fn)):
        glob.glob(partial_fn + '*')
    didn't work for me
    """
    paths = []
    partial_fn = basename(arg)

    dir_ = abspath(dirname(arg))
    # if arg ended in a /, dirname(arg) will be arg without the slash

    if not pexists(dir_):
        dir_ = abspath(dirname(dir_))

    for f in listdir(dir_):
        if f.startswith(partial_fn):
            paths.append(pjoin(dirname(arg), f))
    return paths


def listdir(dir_name):
    """ Ensure that a unicode path is always passed to the 'os' module so that the return value
    is also unicode
    """
    return os.listdir(str(expanduser(dir_name)))
