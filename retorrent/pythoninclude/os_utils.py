#!/usr/bin/python 

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
	if os.path.exists(p):
		s = os.statvfs(p)
		size = s.f_bsize * s.f_bavail
		
		if not units == 'B':
			raise ValueError	
		'''	
		# we have an SI prefix.
		if len(units) == 2 and \
				units[0] in SI_pos:
			
			# might not be round number of MB etc, so use float
			# TODO TODO BUG

			# divide by appropriate 1024.
			pass	
		'''	
		return float(size)


	else:
		# FNF
		return 0

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
