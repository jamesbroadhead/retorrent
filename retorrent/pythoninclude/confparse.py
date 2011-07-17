#!/usr/bin/python

import os
from ConfigParser import ConfigParser

config_paths = [\
	os.path.abspath('./'),\
	os.path.abspath(os.path.expanduser('~/.retorrent/'))
]

stripsymbols ='\'" '

def parse_retorrentconf():
	filename = 'retorrent.conf'

	defaultoptions = { 	'torrentfilesdir':	'~/torrents',		\
						'seeddir':			'~/seed',	\
						'seedtorrentfilesdir':	'~/seed/torrentfiles'
	}
	
	config = ConfigParser(defaultoptions)
	config.read([ os.path.join(p,filename) for p in config_paths])	
	
	output= ( 	config.get('retorrent','torrentfilesdir'), 
				config.get('retorrent','seeddir'),
				config.get('retorrent','seedtorrentfilesdir'))
	
	output = [ os.path.abspath(os.path.expanduser(
			i.strip(stripsymbols))) for i in output ]
	
	return output


def parse_folderconfig():
	
	filename = 'retorrent_folders.conf'

	defaultoptions = { 	'paths':			'',		\
						'treat_as':			'tv',	\
						'should_rename':	'True', \
						'home':				''
	}
	
	treat_as_options = [ 'movies', 'tv', 'files' ]

	config = ConfigParser(defaultoptions)
	config.read([ os.path.join(p,filename) for p in config_paths])	
	
	output = [] 
	
	for category in config.sections():
		
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

	return output 

def parse_fileext_details():
	
	defaultoptions =  { 'type':'movie',\
						'ignore_if_in_filename':'sample' }
	
	filename = 'fileext_details.conf'
	
	config = ConfigParser(defaultoptions)
	config.read([ os.path.join(p,filename) for p in config_paths])	

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

	return output 


def parse_divider_symbols():
	
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

if __name__ == '__main__':
	a = read_folderconfig()

