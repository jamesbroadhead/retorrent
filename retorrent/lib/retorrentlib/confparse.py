#!/usr/bin/python

import os
import shutil

from ConfigParser import ConfigParser
from os.path import expanduser

from logdecorators.tracelogdecorator import tracelogdecorator
from os_utils import os_utils


# TODO: Some object orientation ?
# TODO: retorrent.conf -> use global_content_dirs

config_paths = [\
	os.path.abspath('./'),\
	os.path.abspath(os.path.expanduser('~/.retorrent/')), \
	'/usr/share/retorrent/']


stripsymbols ='\'" '

# Rather than have 2 conf files, have one. 
# [retorrent] section is special, the rest are 'categories'

@tracelogdecorator
def parse_retorrentconf(extra_configdir=''):
	
	if extra_configdir:
		config_paths.insert(0,extra_configdir) 

	filename = 'retorrent.conf'

	defaultoptions = { 	'paths':			'',		\
						'treat_as':			'tv',	\
						'should_rename':	'True', \
						'home':				''}
	
	treat_as_options = [ 'movies', 'tv', 'files' ]

	config = ConfigParser(defaultoptions)
	config.read([ os.path.join(p,filename) for p in config_paths])	

	retorrent_output = ('~/torrents','~/seed','~/seed/torrentfiles')
	retorrent_output = [os.path.expanduser(i) for i in retorrent_output] 
	
	output = [] 
	
	for category in config.sections():
		
		if category == 'retorrent':	
			retorrent_output= (config.get('retorrent','torrentfilesdir'), 
				config.get('retorrent','seeddir'),
				config.get('retorrent','seedtorrentfilesdir'))
			
			retorrent_output = [ os.path.abspath(os.path.expanduser(i.strip(stripsymbols))) for i in retorrent_output ]
		else:	
			# separate by commas, strip quotes
			paths = [ os.path.expanduser(item.strip(stripsymbols)) for item in \
					config.get(category,'paths').split(',') ]
			
			treat_as = 	config.get(category,'treat_as').strip(stripsymbols)
			
			if not treat_as	in treat_as_options:
				print 'CONFIG_WARNING: "'+treat_as+'" is not a valid treat_as setting in category '+category+'. Taking "movies".'	
				treat_as = 'movies'
			
			should_rename = config.getboolean(category,'should_rename')
			
			category_home = config.get(category,'home')
			if category_home == '':
				category_home = os.path.expanduser('~/video/' + category)
			else:
				category_home = os.path.expanduser(category_home)

			item = 	{ 'category':category, \
					'paths':paths,\
					'treat_as':treat_as,\
					'should_rename':should_rename, \
					'home': category_home
			}

			# some nice sorting :-/
			if category == 'movies':
				output = [item] + output
			elif category == 'tv':
				# if #1 is movies then #2
				if output and output[0]['category'] == 'movies':
					output = [output[0],item] + output[1:]
				# else #1
				else:
					output = [item] + output
			else:
				output.append(item)
	
	# file not found
	if not output:
		confdir = os.path.expanduser('~/.retorrent')
		skelfile = 	'/usr/share/retorrent/' + filename + '_skel'
		
		if os.path.exists(skelfile):
			if not os.path.exists(os.path.join(confdir,filename + '_skel')):
				print 'Creating a skeleton $HOME/.retorrent/retorrent.conf, please configure it to your system'
				os_utils.mkdir_p(confdir)
				shutil.copyfile('/usr/share/retorrent/retorrent.conf_skel',os.path.expanduser('~/.retorrent/retorrent.conf_skel'))	
			else:
				print 'Please configure the retorrent.conf_skel in ${HOME}/.retorrent and rename it to '+filename
		else:
			print 'Cannot find '+filename+' or a valid skeleton '+filename+'.'
			print 'Please create and configure ' + \
				os.path.join(confdir,filename) +   \
				' or check your installation.'

	return retorrent_output,output 

def parse_fileext_details(extra_configdir=''):
	
	if extra_configdir:
		config_paths.insert(0,extra_configdir) 

	defaultoptions =  { 'type':'movie',\
						'ignore_if_in_filename':'sample' }
	
	filename = 'fileext_details.conf'
	
	config = ConfigParser(defaultoptions)
	files_read = config.read([ os.path.join(p,filename) for p in config_paths])	
	
	output = [] 
	
	filetypes_goodsizes = {'movie':5120,
							'binaryfile':100,
							'plaintext':4} 	
		
	for fileext in config.sections():
		
		filetype = 	config.get(fileext,'type').split('#')[0].strip(stripsymbols)
		
		if not filetype	in filetypes_goodsizes.keys():
			print 'CONFIG_WARNING: "'+filetype+'" is not a valid type setting for filetype '+filetype+'. Taking "movie".'	
			treat_as = 'movie'
		
		# separate by commas, strip quotes
		ignorestrs = [ os.path.expanduser(item.strip(stripsymbols)) for item in \
				config.get(fileext,'ignore_if_in_filename').split('#')[0].split(',') ]
		
		
		goodsize = filetypes_goodsizes[filetype]
		
		item = 	{ 'fileext':fileext, 
			'filetype':filetype,
			'ignore_if_in_filename':ignorestrs,
			'goodsize' : goodsize
		}
		
		output.append(item)
	
	if not output:
		raise EnvironmentError('Could not locate or load ' + filename + ' and cannot operate without it. A default should be in ' + config_paths[-1] + ', check your installation.')
	
	return output 

def read_fileexts():
	filetypes = parse_fileext_details()
	fileexts = [ f['fileext'] for f in filetypes ]
	return fileexts

def parse_divider_symbols(extra_configdir=''):
	
	if extra_configdir:
		config_paths.insert(0,extra_configdir) 
	
	filename = 'divider_symbols.conf'
	defaultoptions =  { 'symbols' : ' +-_@,' }
	symbols = []	
	config = ConfigParser(defaultoptions)
	config.read([ os.path.join(p,filename) for p in config_paths])	

	for sect in config.sections():
		if sect == 'symbols':
			symb_string = config.get(sect,'symbols')
			# NOT stripsymbols	
			symbols = [ char for char in symb_string.strip("'") ]
		else:
			print 'CONFIG_WARNING: '+filename+' contains the unknown section ['+sect+']'
	
	if symbols == []:
		symbols = [' ', '+', '-', '_', '@', ',']
	
	return symbols

def find_removelist(extra_configdir=''):
	if extra_configdir:
		config_paths.insert(0,extra_configdir) 

	removelist_filename = 'removestrings.list'	
	for path in config_paths:
		filepath = os.path.join(path,removelist_filename)
		if os.path.exists(filepath):
			# check permissions?	
			return filepath

	default_path = os.path.join(os.path.expanduser('~/.retorrent'),removelist_filename)
	
	if not os.path.exists(default_path):
		open(default_path, 'w').close() 
	
	return default_path
