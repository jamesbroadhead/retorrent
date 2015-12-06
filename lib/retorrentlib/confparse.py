#!/usr/bin/python
"""
Parses retorrentconf.py and other files in ~/.retorrent
"""
from __future__ import print_function, unicode_literals

from ast import literal_eval
from ConfigParser import SafeConfigParser
from collections import OrderedDict
from copy import deepcopy
from os.path import abspath, expanduser
from os.path import join as pjoin
from os.path import exists as pexists
import shutil
import sys

import simplejson as json

from redecorators.tracelogdecorator import tracelogdecorator
from os_utils.os_utils import mkdir_p

home_config_dir = abspath(expanduser('~/.retorrent/'))

config_paths = [
    abspath('./'),
    home_config_dir,
    '/usr/share/retorrent/'
]
config_filename = 'retorrentconf.py'

@tracelogdecorator
def parse_retorrentconf(extra_configdir=''):
    #pylint: disable=too-many-branches,too-many-locals
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
        'torrentfilesdir'      : '~/torrents/torrentfiles',
        'seeddir'              : '~/seed',
        'seedtorrentfilesdir'  : '~/seed/torrentfiles',
        'content_root_paths'   : [],
        'symlink_path'         : '~/video',
        'smbsafe_symlink_path' : '~/smbsafevideo'
    }

    if not validate_config(config):
        sys.exit(1)

    global_conf = deepcopy(global_defaults)
    global_conf.update(config['global'])

    for k, v in global_conf.items():

        if isinstance(v, basestring):
            global_conf[k] = abspath(expanduser(v))
        elif isinstance(v, list):
            global_conf[k] = [abspath(expanduser(i)) for i in v]
        else:
            print('Unknown value type under global/%s' % (k,))

    category_defaults = {
        'symlink_path'        : '',
        'smbsafe_symlink_path': '',
        'content_paths'       : [],
        'treat_as'            : 'tv',
        'should_rename'       : 'True'
    }
    treat_as_options = ['movies', 'tv', 'files']

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

        # use global options if no specific rules
        for opt in ['symlink_path', 'smbsafe_symlink_path']:
            if not category_conf[opt]:
                category_conf[opt] = pjoin(global_conf[opt], category)

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
        print('Please create and configure %s or check your installation. ' % (
            pjoin(confdir, config_filename)))


def validate_config(config):
    ok = True
    if not 'global' in config:
        ok = False
        print("Config must have a 'global' key")
    if not 'content_root_paths' in config.get('global', {}):
        ok = False
        print("Config must have 'content_root_paths' under 'global'")
    if not 'categories' in config:
        ok = False
        print("Config must have a 'global' key")
    if not config.get('categories', []):
        ok = False
        print("Must define a single category under 'categories'")
    return ok



def parse_fileext_details(extra_configdir=''):

    if extra_configdir:
        config_paths.insert(0, extra_configdir)

    filename = 'fileext_details.json'

    for prepath in config_paths:
        path = pjoin(prepath, filename)
        if pexists(path):
            filepath = path

    if not filepath:
        raise EnvironmentError('Could not locate or load %s and cannot operate' % (filename,) +
                               'without it. A default should be in %s' % (config_paths[-1],) +
                               ', check your installation.')

    with open(filepath) as fh:
        content = dict(json.loads(fh.read()))

    default_filetypes_goodsizes = {
        'movie'     : 5120,
        'binaryfile':  100,
        'plaintext' :    4
    }

    # mutates parsed `content` to inject defaults. urgh.
    for _, conf in content.items():
        if not 'filetype' in conf:
            conf['filetype'] = 'movie'

        if not conf['filetype'] in default_filetypes_goodsizes:
            raise EnvironmentError('"filetype" in %r stanzas must be one of %r. Got: %r' % (
                filename, default_filetypes_goodsizes.keys(), conf['filetype']))

        if not 'ignore_if_in_filename' in conf:
            conf['filetype'] = ['sample']

        if not 'goodsize' in conf:
            conf['goodsize'] = default_filetypes_goodsizes[conf['filetype']]

    return content


def parse_divider_symbols(extra_configdir=''):

    if extra_configdir:
        config_paths.insert(0, extra_configdir)

    filename = 'divider_symbols.conf'
    defaultoptions = {'symbols' : ' +-_@,'}
    symbols = []
    config = SafeConfigParser(defaultoptions)
    config.read([pjoin(p, filename) for p in config_paths])

    for sect in config.sections():
        if sect == 'symbols':
            symb_string = config.get(sect, 'symbols')
            # NOT stripsymbols
            symbols = [char for char in symb_string.strip("'")]
        else:
            print('CONFIG_WARNING: '+filename+' contains the unknown section ['+sect+']')

    if symbols == []:
        symbols = [' ', '+', '-', '_', '@', ',']

    return symbols

def find_configfile(filename, extra_configdir=''):
    default_path = pjoin(expanduser('~/.retorrent'), filename)
    if extra_configdir:
        config_paths.insert(0, extra_configdir)

    for path in config_paths:
        filepath = pjoin(path, filename)
        if pexists(filepath):
            # check permissions?
            return filepath

    # nothing found - touch an empty config return that
    touch_default(default_path)
    return default_path

def touch_default(path):
    if not pexists(path):
        open(path, 'w').close()

def find_removelist(extra_configdir=''):
    return find_configfile('removestrings.list', extra_configdir)

def find_pretokenized_removelist(extra_configdir=''):
    return find_configfile('pretokenized_removestrings.list', extra_configdir)

def get_torrentfilesdir(global_conf=None):
    if global_conf is None:
        global_conf, _ = parse_retorrentconf()
    return global_conf['torrentfilesdir']
