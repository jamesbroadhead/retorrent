#!/usr/bin/env python
"""
retorrent - a media management tool

Author: James Broadhead jamesbroadhead@gmail.com
"""
from __future__ import print_function

import logging
from optparse import OptionParser
import os
from os.path import expanduser, isdir
from os.path import join as pjoin
import sys

from ..retorrenter import check_result, Retorrenter


def main():
    options, argv = parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logdir = expanduser('~/.retorrent')
    if not isdir(logdir):
        os.makedirs(logdir)
    logfile_handler = logging.FileHandler(pjoin(logdir, 'retorrent.log'))
    logger.addHandler(logfile_handler)

    if options.debug:
        stdout_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stdout_handler)

    feature_flags = {'old_torrentfile_detection': options.old_torrentfile_detection}

    r = Retorrenter(options.configdir, debug=options.debug, feature_flags=feature_flags)

    # get args (folders / files which are 100% downloaded.
    command_bundles = r.handle_args(argv)

    if options.pretend:
        pretend_command_bundles(command_bundles)
    else:
        execute_command_bundles(command_bundles)


def pretend_command_bundles(command_bundles):
    for bundle in command_bundles:
        for sub_cmd in bundle['commands']:
            os.system('echo %s' % (sub_cmd.encode('utf-8'),))


def execute_command_bundles(command_bundles):
    for bundle in command_bundles:
        failed = False
        for sub_cmd in bundle['commands']:
            try:
                retval = os.system(sub_cmd.encode('utf-8'))
            except Exception as e:
                print(e)
                retval = -1
            bundle['commands_run'].append(sub_cmd)
            if not retval == 0:
                failed = True
                break

        if not check_result(bundle, failed) or failed:
            break
    if command_bundles:
        os.system('symlinker')


def parse_args():
    parser = OptionParser()

    parser.add_option('-c',
                      '--config-dir',
                      help='Specify alternate config dir',
                      dest='configdir',
                      default='')

    parser.add_option('-d',
                      '--debug',
                      help='Print debug messages (where implemented)',
                      action='store_true',
                      dest='debug',
                      default=False)

    parser.add_option('-p',
                      '--pretend',
                      help='Build commands, but do not run them',
                      action='store_true',
                      dest='pretend',
                      default=False)

    parser.add_option('-t',
                      '--old-torrentfile-detection',
                      help='Use old, not new torrentfile behaviour',
                      action='store_true',
                      dest='old_torrentfile_detection',
                      default=False)

    options, args = parser.parse_args()
    return options, args


def print_optionstructions():
    print('\n'.join([
        '<WORD> will remove WORD this time only', '-<WORD> will add WORD to the REMOVE_LIST',
        '"+<WORD>" will set the dir to be WORD'
    ]))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
