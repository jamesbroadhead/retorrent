#!/usr/bin/python 

import platform
import errno
import os

SI_pos = [ 'k','M','G','T' ]
def freespace(p,units='B'):
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
		ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
		space = free_bytes.value
	else:	
		s = os.statvfs(p)
		
		# MacOS compat; 
		# 	f_bsize is the preferred block size while .f_frsize is the 
		#	fundamental block size
		
		space = s.f_frsize * s.f_bavail
	
	if not units in SI_pos:
		raise ValueError	
	
	divisor= 1024 * SI_pos.index(units)
		
	if divisor > 0.01:
		space = float(size) / divisor
	
	return space

def enough_space(orig_paths,proposed_path):
	
	filesize_B = sum([os.path.getsize(orig_path) for orig_path in orig_paths ])	
	
	proposed_path = os.path.expanduser(proposed_path)
	if not os.path.exists(proposed_path):
		proposed_path = os.path.dirname(proposed_path.rstrip('/'))
		print proposed_path
	
	if filesize_B < freespace(proposed_path):
		return True
	else:
		proposed_device = device_number(proposed_path)
		same_drive = [ proposed_device == device_number(path) for path in orig_paths ]
		for i in same_drive:
			if not i: return False
		return True

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
