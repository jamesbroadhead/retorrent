#!/usr/bin/python 

import platform
import errno
import os

from logdecorators.tracelogdecorator import tracelogdecorator

SI_pos = [ 'k','M','G','T' ]
def freespace(p,si_prefix=''):
    """
    Returns the number of free bytes on the drive that ``p`` is on
    
    I use the f_bavail attribute instead of f_bfree, since the latter 
        includes blocks that are reserved for the the super-user.s use.
        I'm not sure, however, on the distinction between f_bsize and f_frsize.
    
    From: http://atlee.ca/blog/2008/02/23/getting-free-diskspace-in-python/
    """
        
    # http://stackoverflow.com/questions/51658/cross-platform-space-remaining-on-volume-using-python
    if platform.system() == 'Windows':
        import ctypes
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(p), None, None, ctypes.pointer(free_bytes))
        space = free_bytes.value
    else:    
        s = os.statvfs(p)
        
        # MacOS compat; 
        #     f_bsize is the preferred block size while .f_frsize is the 
        #    fundamental block size
        
        space = s.f_frsize * s.f_bavail
    
    if si_prefix:
        if not si_prefix in SI_pos:
            raise ValueError('Invalid SI prefix')
        divisor= 1024 * SI_pos.index(si_prefix)
        space = float(space) / divisor
    
    return space

@tracelogdecorator
def enough_space(orig_paths,proposed_path):
    proposed_path = os.path.expanduser(proposed_path)
    # first check if they're on the same volume
    if same_volume(orig_paths,proposed_path):
        return True
    
    proposed_path = os.path.expanduser(proposed_path)
    
    filesize_B = sum([os.path.getsize(orig_path) for orig_path in orig_paths ])    
    if not os.path.exists(proposed_path):
        proposed_path = os.path.dirname(proposed_path.rstrip('/'))
    
    if filesize_B < freespace(proposed_path):
        return True
    return False

@tracelogdecorator
def same_volume(orig_paths,proposed_path):
    pp = proposed_path        
    
    # Should only be one loop 
    #    (eg. video/tv/foo -> video/tv)
    while not os.path.exists(pp):
        pp = os.path.dirname(pp)
    prop_dev = device_number(pp)    
    
    for p in orig_paths:
        if not prop_dev == device_number(p):
            return False
    return True

@tracelogdecorator
def device_number(path):
    return os.stat(os.path.expanduser(path)).st_dev

def hostname():
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
    if len(path) == 0:
        return ''
    
    return os.path.basename(path.strip('/'))

def str2utf8(a):
    if type(a) == type(u'unicode'):
        u = a
    else:
        u = unicode(a,'utf-8', errors='ignore')    
    return u

def diskspace_used(f,si='kiB'):
    
    filestat = os.stat(f)
    disk_filesize_b = filestat.st_blocks*filestat.st_blksize
    
    if si == 'kiB':
        return disk_filesize_b/(8*1024)
    elif si == 'B':
        return disk_filesize_b/(8)
    else: # kiB
        return disk_filesize_b/(8*1024)

def sym_sametarget(a,b):
    return os.path.realpath(a) == os.path.realpath(b)
