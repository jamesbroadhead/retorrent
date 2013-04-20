#!/usr/bin/python
"""
Parses retorrentconf.py and other files in ~/.retorrent
"""

from __future__ import print_function
from ast import literal_eval
from ConfigParser import SafeConfigParser
from collections import OrderedDict
from copy import deepcopy
from os.path import abspath, expanduser
from os.path import join as pjoin
from os.path import exists as pexists
import shutil
import sys

from logdecorators.tracelogdecorator import tracelogdecorator
from os_utils.os_utils import mkdir_p

# XXX: Use symlink_root_path in retorrent somewhere ...

config_paths = [
    abspath('./'),
    abspath(expanduser('~/.retorrent/')),
    '/usr/share/retorrent/'
]
config_filename = 'retorrentconf.py'

@tracelogdecorator
def parse_retorrentconf(extra_configdir=''):
    config = {}
    for cp in [extra_configdir] + config_paths:
        path = pjoin(cp, config_filename)
        if pexists(path):
            with open(path) as fh:
                config = literal_eval(fh.read())

    if not config:
        write_default_config()
        sys.exit(1)

    global_defaults = {
        'torrentfilesdir'     : '~/torrents/torrentfiles',
        'seeddir'             : '~/seed',
        'seedtorrentfilesdir' : '~/seed/torrentfiles',
        'content_root_paths'  : [],
        'symlink_root_path'   : '~/video'
    }

    if not validate_config(config):
        sys.exit(1)

    global_conf = deepcopy(global_defaults)
    global_conf.update(config['global'])

    for k, v in global_conf.items():
        if type(v) == str:
            global_conf[k] = abspath(expanduser(v))
        elif type(v) == list:
            global_conf[k] = [ abspath(expanduser(i)) for i in v ]
        else:
            print('Unknown value type under global/%s' % (k,))

    category_defaults = {
        'symlink_path' : '',
        'content_paths': [],
        'treat_as'     : 'tv',
        'should_rename': 'True'
    }
    treat_as_options = [ 'movies', 'tv', 'files' ]

    categories = config['categories']

    for category in categories:

        category_conf = deepcopy(category_defaults)
        category_conf.update(categories[category])

        # inject global paths
        for p in global_conf['content_root_paths']:
            content_path = pjoin(p, category)
            if not content_path in category_conf['content_paths']:
                category_conf['content_paths'].append(content_path)

        # validate treat_as
        if not category_conf['treat_as'] in treat_as_options:
            print("Illegal value for ['categories']['%s']['treat_as']" %(category,))
            sys.exit(1)

        if not category_conf['symlink_path']:
            category_conf['symlink_path'] = pjoin(global_conf['symlink_root_path'],
                                                  category)

        categories[category] = category_conf

    ordered_categories = OrderedDict()
    keys = set(categories.keys())

    # insert special keys first
    for k in ['movies', 'tv']:
        if k in keys:
            ordered_categories[k] = categories[k]
            keys.remove(k)

    # then the rest, in order
    keys = list(keys)
    keys.sort()
    for k in keys:
        ordered_categories[k] = categories[k]

    return global_conf, ordered_categories

def write_default_config():
    confdir = expanduser('~/.retorrent')
    skelfile = '/usr/share/retorrent/' + config_filename + '_skel'

    if pexists(skelfile):
        if not pexists(pjoin(confdir, config_filename + '_skel')):
            print('Creating a skeleton $HOME/.retorrent/retorrent.conf, ' +
                  'please configure it to your system')
            mkdir_p(confdir)
            shutil.copyfile('/usr/share/retorrent/retorrent.conf_skel',
                            expanduser('~/.retorrent/retorrent.conf_skel'))
        else:
            print('Please configure the retorrent.conf_skel in ${HOME}/.retorrent ' +
                  'and rename it to '+config_filename)
    else:
        print('Cannot find '+config_filename+' or a valid skeleton '+config_filename+'.')
        print('Please create and configure %s or check your installation. '
                % (pjoin(confdir, config_filename)))


def validate_config(config):
    ok = True
    if not 'global' in config:
        ok = False
        print("Config must have a 'global' key")
    if not 'content_root_paths' in config.get('global', {}):
        failed = False
        print("Config must have 'content_root_paths' under 'global'")
    if not 'categories' in config:
        failed = False
        print("Config must have a 'global' key")
    if not config.get('categories', []):
        failed = False
        print("Must define a single category under 'categories'")
    return ok



def parse_fileext_details(extra_configdir=''):

    if extra_configdir:
        config_paths.insert(0, extra_configdir)

    defaultoptions =  { 'type':'movie',
                        'ignore_if_in_filename':'sample' }

    filename = 'fileext_details.conf'

    config = SafeConfigParser(defaultoptions)

    file_read = config.read(pjoin(cp, filename) for cp in config_paths)

    if not file_read:
        raise EnvironmentError('Could not locate or load ' + filename + ' and cannot operate ' +
                               'without it. A default should be in ' + config_paths[-1] +
                               ', check your installation.')

    output = []
    filetypes_goodsizes = {'movie'     : 5120,
                           'binaryfile':  100,
                           'plaintext' :    4}
    stripsymbols = '\'" '
    for fileext in config.sections():

        filetype = config.get(fileext,'type').split('#')[0].strip(stripsymbols)

        if not filetype in filetypes_goodsizes.keys():
            print('CONFIG_WARNING: "'+filetype+'" is not a valid type setting for filetype ' +
                  filetype+'. Taking "movie".')

        # separate by commas, strip quotes
        ignorestrs = [ expanduser(item.strip(stripsymbols)) for item in
                config.get(fileext,'ignore_if_in_filename').split('#')[0].split(',') ]


        goodsize = filetypes_goodsizes[filetype]

        item =     { 'fileext':fileext,
            'filetype':filetype,
            'ignore_if_in_filename':ignorestrs,
            'goodsize' : goodsize
        }

        output.append(item)

    return output

def read_fileexts():
    filetypes = parse_fileext_details()
    fileexts = [ f['fileext'] for f in filetypes ]
    return fileexts

def parse_divider_symbols(extra_configdir=''):

    if extra_configdir:
        config_paths.insert(0, extra_configdir)

    filename = 'divider_symbols.conf'
    defaultoptions =  { 'symbols' : ' +-_@,' }
    symbols = []
    config = SafeConfigParser(defaultoptions)
    config.read([ pjoin(p, filename) for p in config_paths])

    for sect in config.sections():
        if sect == 'symbols':
            symb_string = config.get(sect,'symbols')
            # NOT stripsymbols
            symbols = [ char for char in symb_string.strip("'") ]
        else:
            print('CONFIG_WARNING: '+filename+' contains the unknown section ['+sect+']')

    if symbols == []:
        symbols = [' ', '+', '-', '_', '@', ',']

    return symbols

def find_removelist(extra_configdir=''):
    if extra_configdir:
        config_paths.insert(0, extra_configdir)

    removelist_filename = 'removestrings.list'
    for path in config_paths:
        filepath = pjoin(path, removelist_filename)
        if pexists(filepath):
            # check permissions?
            return filepath

    default_path = pjoin(expanduser('~/.retorrent'), removelist_filename)

    if not pexists(default_path):
        open(default_path, 'w').close()

    return default_path
