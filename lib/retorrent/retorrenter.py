""" retorrent.retorrenter """

from __future__ import unicode_literals

from copy import deepcopy
import logging
import os
from os.path import abspath, basename, expanduser, isdir, realpath
from os.path import exists as pexists
from os.path import join as pjoin
import traceback

from difflib import SequenceMatcher

from redecorators.tracelogdecorator import tracelogdecorator
from os_utils.os_utils import enough_space, listdir, myglob, str2utf8
from os_utils.textcontrols import bold

from .confparse import get_torrentfilesdir, parse_divider_symbols, parse_fileext_details
from .confparse import parse_retorrentconf
from .debugprinter import Debugprinter
from .filenamer import Filenamer
from .find_tfile import tfile_from_filename
from .optionator import optionator, eqoptionator, CANCEL

RECALCULATE = '-'
log = logging.getLogger("app")


class Retorrenter(object):
    #pylint:disable=too-many-instance-attributes,too-many-public-methods
    commands = None
    dest_dirpath = None
    dest_folder = None
    dest_category = None
    dest_series_folder = None
    filenamer = None

    # self.expected_dirs exists for the case: ./retorrent a.e01.avi a.e02.avi
    expected_dirs = []

    def __init__(self, configdir='', debug=False, feature_flags=None):
        self.configdir = configdir

        self.debug = debug
        self.debugprinter = Debugprinter()

        self.feature_flags = feature_flags
        if feature_flags is None:
            self.feature_flags = {}
        self.global_conf, self.categories = parse_retorrentconf(self.configdir)
        self.filetype_definitions = parse_fileext_details(self.configdir)
        self.divider_symbols = parse_divider_symbols(self.configdir)

    def debugprint(self, txt, listol=None):
        self.debugprinter.debugprint(txt, listol)

    def reset_env(self):
        # The category folder (movies, tv ... )
        self.dest_category = ''
        self.dest_folder = ''
        self.dest_series_folder = ''
        # The series or movie-name folder
        self.dest_dirpath = ''

        self.filenamer = Filenamer(self.divider_symbols, self.filetype_definitions)

    def handle_args(self, arguments):
        """
        @return a list of command_bundles
        """
        content = []
        for a in arguments:
            if pexists(a):
                content.append(a.decode('utf-8'))
            else:
                paths = myglob(a)
                content.extend([p.decode('utf-8') for p in paths if pexists(p)])

        content.sort()
        if not content:
            print 'No content found'
            return []

        self.commands = []
        for c in content:
            # TODO: Could really do with removing this ...
            self.reset_env()

            try:
                commandset = self.handle_content(c)
                if commandset:
                    self.commands.append(commandset)
            except Exception as e:
                # parsing one arg failed -- proceed with the rest
                print e
                print traceback.format_exc()
                log.error(e)
        return self.commands

    def handle_content(self, content):
        """
        Take a path to new content, either a file or a directory, and return a command bundle,
        which will cause the content to be moved to a permanent home, usually being renamed in
        the process. These homes are defined in retorrentconf.py, and the content will be moved
        to:
        mv <original_filename> => <home>/<category>/<filename>
        mv <original_filename> => <home>/<category>/<dest_dirname>/<filename>
        mv <original_dirname>  => <home>/<category>/<dest_dirname>/<filename>

        If the user chooses to seed the content, the torrentfile will be moved in to a
        seed-torrentfile directory, and symlinks from the new content paths to the original
        filenames in a seeding directory will be created
        eg.
        ln -s <home>/<category>/<filename>                => <seeddir>/<original_filename>
        ln -s <home>/<category>/<dest_dirname>/<filename> => <seeddir>/<original_filename>
        ln -s <home>/<category>/<dest_dirname>/<filename> => <seeddir>/<original_dirname>/...
        """
        # pylint: disable=too-many-branches,too-many-return-statements
        print "|\n|\n|\n|"
        print 'For: %s' % (content,)

        content_abspath = abspath(content)

        # get a list of files to keep
        # NOTE: These are only those of the interesting files
        content_details = self.find_files_to_keep(content_abspath)

        orig_paths = content_details['orig_paths']
        orig_foldername = content_details['orig_foldername']

        self.filenamer.set_num_interesting_files(len(orig_paths))

        if len(orig_paths) == 0:
            print "No interesting files found! Skipping!"
            return

        self.debugprint("Dirpath before autoset: " + self.dest_dirpath)

        possible_series_foldernames = [
            self.filenamer.convert_filename(basename(orig_paths[0]), True),
            self.filenamer.convert_filename(orig_foldername, True)
        ]
        possible_series_foldernames = [i for i in possible_series_foldernames if i]

        self.autoset_dest_dirpath(possible_series_foldernames, orig_paths)
        self.debugprint('DestFolder after autoset: ' + self.dest_folder)
        self.debugprint("Dirpath after autoset: " + self.dest_dirpath)

        if not self.dest_category:
            self.manually_set_category(content, orig_paths)

            if not self.dest_category:
                print "cancelled..."
                return
            else:
                # recurse
                return self.handle_content(content)

        # At this point, self.dest_category is set.
        self.filenamer.set_movie(self.is_movie())

        if self.dest_folder == '':
            # not enough space :(
            print "!!! Can't find enough space in any of that category to proceed!"
            print 'Free some disk space, or add another location.'
            return

        self.dest_folder = expanduser(self.dest_folder)
        self.dest_dirpath = expanduser(self.dest_dirpath)

        # At this point : self.dest_folder is set. self.dest_dirpath may not be.
        # 2013-04: ... but what is in each of them ... :(
        # single movie -> both are <path>/movies

        self.debugprint('About to generate dest_dirpath; ' + self.dest_dirpath)
        if self.categories[self.dest_category]['should_rename']:
            if not self.dest_dirpath:
                self.dest_dirpath = self.ask_for_dest_dirpath(
                    len(orig_paths), possible_series_foldernames)
                if not self.dest_dirpath:
                    print "Didn't set a directory - failing"
                    return
        else:
            self.dest_dirpath = pjoin(self.dest_folder, orig_foldername)

        # Now map the original paths to destination paths
        # (Although this duplicates the 'should_rename' check, let's separate concerns

        if self.categories[self.dest_category]['should_rename']:
            rename_map = self.build_rename_map(content_details, possible_series_foldernames)

            if rename_map == RECALCULATE:
                # User added a term to filter. Recurse. (this is a horrible model...)
                return self.handle_content(content)
            elif not rename_map:
                # User cancelled
                return
        else:
            print "Not renaming files"

            rename_map = {p: pjoin(self.dest_dirpath, basename(p)) for p in orig_paths}

        # Check for existing files, abort if found
        already_exists = [dst for _src, dst in rename_map.items() if pexists(dst)]
        if already_exists:
            print 'Some paths already exist, aborting.'
            for ae in sorted(already_exists):
                print '%s' % (ae,)
            return

        return self.build_command_bundle(content_details, rename_map)

    def set_num_interesting_files(self, num_interesting_files):
        self.filenamer.set_num_interesting_files(num_interesting_files)

    def autoset_dest_dirpath(self, possible_series_foldernames, orig_paths):
        """
        dest_dirpath is the 'series name' or similar folder inside the
            category folder
        """

        self.debugprint('retorrenter.autoset_dest_dirpath(%r)' % (possible_series_foldernames,))

        if self.dest_category:
            # the dest category is already set from somewhere else
            categories = [(self.dest_category, self.categories[self.dest_category])]
        else:
            categories = self.categories.items()

        for category, details in categories:
            for cat_folder in details['content_paths']:
                for poss_series_folder in possible_series_foldernames:
                    possible_path = expanduser(pjoin(cat_folder, poss_series_folder))
                    self.debugprint('Looking for ' + possible_path)
                    if os.path.exists(possible_path) or possible_path in self.expected_dirs:
                        self.dest_category = category

                        self.dest_series_folder = poss_series_folder
                        if enough_space(orig_paths, possible_path):
                            self.dest_folder = cat_folder
                            self.dest_dirpath = possible_path
                        else:
                            # Not enough space, but we have the series_folder.
                            # Lets try another disk, or fail

                            # 2013-04: commenting this for testing...
                            # self.dest_category['paths'].remove(cat_folder)
                            self.autoset_equivalent_dest_folder(orig_paths)
                        return

    def dest_category_paths(self):
        return self.categories[self.dest_category]['content_paths']

    def autoset_equivalent_dest_folder(self, orig_paths):
        self.debugprint('Trying to create an eqivalent dest_folder for %s' %
                        (pjoin(self.dest_category, self.dest_series_folder)))

        if self.dest_category and not self.dest_series_folder == "":
            # let's create an equivalent dir on a different drive
            for cat_folder in self.dest_category_paths():
                possible_path = pjoin(cat_folder, self.dest_series_folder)

                self.debugprint('Checking:' + possible_path)
                self.debugprint('Equivalent candidate: ' + possible_path)

                if os.path.exists(possible_path) and enough_space(orig_paths, possible_path):
                    msg = 'Equivalent candidate exists already and has enough space: %s'
                    self.debugprint(msg % (possible_path,))

                    self.dest_folder = cat_folder
                    self.dest_dirpath = possible_path
                    return

            for cat_folder in self.dest_category_paths():
                self.debugprint('Equivalent candidate has enough space: ' + possible_path)
                possible_path = pjoin(cat_folder, self.dest_series_folder)

                if enough_space(orig_paths, possible_path):
                    self.dest_folder = cat_folder
                    self.dest_dirpath = possible_path
                    return

            # There are no drives in the list with enough disk space ... :(
            # TODO: Bail here.

        else:
            # we don't have enough info to make the dir on a different drive
            pass

    def manually_set_category(self, argument, orig_paths):
        question = "Destination for " + argument
        dest_category_name = optionator(question, self.categories.keys() + [CANCEL])

        if dest_category_name in self.categories:
            self.dest_category = dest_category_name
            self.autoset_dest_folder_from_dest_category(orig_paths)
            return

        if not dest_category_name:
            return ''
        else:
            print 'Error -- category was unrecognised!'
            self.manually_set_category(argument, orig_paths)

    @tracelogdecorator
    def autoset_dest_folder_from_dest_category(self, orig_paths):
        if self.dest_category:
            for path in self.categories[self.dest_category]['content_paths']:
                self.debugprint('Possible path: ' + path)
                if not os.path.exists(path):
                    print "Warning: Config contains a path that doesn't exist: %s" % (path,)
                elif enough_space(orig_paths, path):
                    self.debugprint('Setting dest_folder to: ' + path)
                    self.dest_folder = path
                    return

    def ask_for_dest_dirpath(self, num_interesting_files, possible_series_foldernames):

        self.debugprint('retorrenter.ask_for_dest_dirpath()')
        # gen dest paths from these foldernames

        # if a movie has +1 files, need a folder. All else might need a folder
        if self.is_movie() and num_interesting_files == 1:
            self.debugprint('ask_for_dest_dirpath: This is a movie, no need for a folder')
            return self.dest_folder
        else:

            if self.is_movie() or num_interesting_files > 1:
                dirpath_q = "What foldername should we use?"
                dirpath_q_opts = possible_series_foldernames + [CANCEL]
            else:
                dirpath_q = "Is this a series? If so, use what folder name?"
                dirpath_q_opts = possible_series_foldernames + [CANCEL]

            dirpath_ans = self.pose_question(dirpath_q, dirpath_q_opts)

            if not dirpath_ans == RECALCULATE:
                return pjoin(self.dest_folder, dirpath_ans)
            else:
                # a new removeitem has been added - regenerate psf
                possible_series_foldernames = [
                    self.filenamer.convert_filename(item, True)
                    for item in possible_series_foldernames
                ]

                return self.ask_for_dest_dirpath(num_interesting_files, possible_series_foldernames)

    def pose_question(self, question, options):
        # Note: returns RECALCULATE ('-') if a recurse is needed

        answer = eqoptionator(question, options)

        if answer in options or answer == '':
            return answer
        elif answer.startswith('+'):
            return answer[1:]
        elif answer.startswith('-'):
            self.filenamer.add_to_removeset(answer[1:])
            return RECALCULATE
        else:
            self.filenamer.add_to_tmp_removeset(answer)
            return RECALCULATE

    def find_files_to_keep(self, content_abspath):
        """
        For all files, needs to return:
            Foldername (if arg is torrent/$FOLDER )
                orig_foldername neither begins nor ends with slashes
            Intermediate ( torrent/$FOLDER/$INTERMED/ )
                elements of orig_intermeds elements have neither beginning nor ending slashes
            Files ( torrent.$FOLDER/$INTERMED/$FILE )
        """
        # pylint: disable=too-many-locals
        file_paths = []
        file_names = []
        intermeds = []
        # if (folder), figure out which files are the movie
        if os.path.isdir(content_abspath):

            orig_foldername = os.path.basename(content_abspath)

            for (path, _dirs, files) in os.walk(content_abspath):
                for f in files:
                    file_path = path + "/" + f
                    thisfile_intermed = path[len(content_abspath) + 1:]
                    if os.path.exists(file_path):
                        file_paths += [os.path.abspath(file_path)]
                        file_names += [os.path.basename(file_path)]
                        intermeds += [thisfile_intermed]
                    else:
                        print "Internal error - built a path, then file didn't exist(?)"
        else:
            orig_foldername = ""  # it's a file, flat in ~/torrents
            if os.path.exists(content_abspath):
                file_path = content_abspath
                file_paths = [os.path.abspath(file_path)]
                file_names = [os.path.basename(file_path)]
                intermeds = [""] * len(file_names)

        # remove files that aren't of interest
        (filepaths_to_keep, intermeds_to_keep, filenames_to_keep,
         num_discarded_files) = self.get_movies_and_extras(file_paths, intermeds, file_names)

        content_details = {
            'content_abspath': content_abspath,
            'orig_paths': filepaths_to_keep,
            'orig_foldername': orig_foldername,
            'orig_intermeds': intermeds_to_keep,
            'orig_filenames': filenames_to_keep,
            'num_discarded_files': num_discarded_files
        }

        return content_details

    # strip uninteresting files from the lists
    def get_movies_and_extras(self, list_of_filepaths, list_of_intermeds, list_of_filenames):

        filepaths_to_keep = []
        intermeds_to_keep = []
        filenames_to_keep = []
        num_discarded_files = 0

        for filepath, intermed, filename in zip(list_of_filepaths, list_of_intermeds,
                                                list_of_filenames):

            if self.is_of_interest(filepath, intermed, filename):
                filepaths_to_keep += [filepath]
                intermeds_to_keep += [intermed]
                filenames_to_keep += [filename]
            else:
                #print "Skipping ",os.path.basename(filepath)
                num_discarded_files += 1

        return filepaths_to_keep, intermeds_to_keep, filenames_to_keep, num_discarded_files

    @tracelogdecorator
    def is_of_interest(self, file_path, intermeds, filename):
        """
        @param intermeds: a string containing the intermediate path between the target passed to
        the cli and this particular file. abspath(pjoin(intermeds, filename) == file_path
        """
        logging.info('is_of_interest: %s', self.global_conf['ignore_if_in_path'])

        for ignore_if_in_path in self.global_conf['ignore_if_in_path']:
            if ignore_if_in_path.lower() in intermeds.lower():
                logging.info(
                    'is_of_interest: ignoring because its intermediate path contains an excluded substring (%s, %s, %s)',
                    file_path, intermeds, filename)
                return False

        _path, extension = os.path.splitext(file_path)
        # trim the . from the extension for matching
        extension = extension[1:].lower()

        if extension in self.filetype_definitions:
            details = self.filetype_definitions[extension]

            # if the filename has something which excludes it, skip it
            # eg. 'sample'
            for exclude in details['ignore_if_in_filename']:
                if exclude == '':
                    continue
                if not filename.lower().find(exclude.lower()) == -1:
                    # this file has a phrase which excludes it
                    self.debugprint(filename + ' contains a phrase which excludes it')
                    return False

            filestat = os.stat(file_path)
            # this will actually get the size of all the blocks, not the space used.
            # Close enough ... :P
            disk_filesize_kB = filestat.st_blocks * filestat.st_blksize / (8 * 1024)

            if disk_filesize_kB > details['goodsize']:
                return True
            else:
                logging.info('Size: %rkB < %rkB for: %r', disk_filesize_kB, details['goodsize'],
                             file_path)
        logging.info(filename + " didn't trigger any interest ...")
        return False

    def is_movie(self):
        if self.dest_category:
            return self.categories[self.dest_category]['treat_as'] == 'movies'
        return False

    def old_find_torrentfile(self, the_path):
        # get the file / foldername (not necc. the same as the arg itself
        split_path = the_path.rsplit('/')
        arg_name = split_path[-1]

        the_torrentfiles = [
            f for f in os.listdir(get_torrentfilesdir(self.global_conf)) if not f == '.keep'
        ]
        exclude = [c['torrentfile'] for c in self.commands]

        tfiles = []
        for tfile in the_torrentfiles:
            if tfile in exclude:
                continue
            cf = self.filenamer.convert_filename(
                tfile.rstrip('torrent').rstrip('.'), True, interactive=False)

            score = SequenceMatcher('', str2utf8(arg_name), str2utf8(cf)).ratio()

            tfiles += [{'filename': tfile, 'conv_filename': cf, 'score': score}]

        tfiles = sorted(tfiles, self.compare_scored_tfiles)

        chosen_torrentfile = optionator('For: ' + arg_name, [t['filename']
                                                             for t in tfiles] + [CANCEL])

        return chosen_torrentfile

    @staticmethod
    def compare_scored_tfiles(A, B):
        cmp_ = cmp(B['score'], A['score'])

        if not cmp_ == 0:
            return cmp_
        return cmp(A['filename'], B['filename'])

    def filename_from_foldername(self, possible_series_foldernames, converted_filename):
        """
        @param filename : An already-converted filename,
                            to extract epno, checksum and fileext from
        @param possible_series_foldernames : A list of foldernames to base the conversions on.
                            This either contains [], [foo] or [foo, bar]
                            Where foo is a string based on the first filename encountered
                            And bar is a string based on the folder passed, if the arg was a
                            folder
        """
        if len(possible_series_foldernames) > 1:
            # Use the string generated from the foldername
            src_foldername = possible_series_foldernames[1]
        elif len(possible_series_foldernames) > 0:
            # Use the string generated from the first filename
            src_foldername = possible_series_foldernames[0]
        else:
            src_foldername = ''

        return self.filenamer.gen_final_filename_from_foldername(src_foldername, converted_filename)

    def build_rename_map(self, content_details, possible_series_foldernames):
        #pylint: disable=too-many-branches,too-many-locals,too-many-statements
        content_abspath = content_details['content_abspath']
        orig_paths = content_details['orig_paths']

        # At this point, self.dest_dirpath contains the full folder path
        self.debugprint('Final dest_dirpath=' + self.dest_dirpath)
        ##################################
        ## Now to rename the filenames
        ##################################
        # create output paths based on the filenames

        # TODO: Create a map of src -> [poss_dest, poss_dest]
        # TODO: verify that for a set of poss_dests, there are no duplicates
        mutual = {}
        multiple = {}
        for path in orig_paths:
            src_filename = basename(path)
            filename_from_filename = self.filenamer.convert_filename(src_filename, False)
            relpath_from_filename = pjoin(basename(self.dest_dirpath), filename_from_filename)
            path_from_filename = pjoin(self.dest_dirpath, filename_from_filename)
            self.debugprint('path_from_filename = %s' % self.dest_dirpath)

            path_from_foldername = ''
            if isdir(content_abspath):
                filename_from_foldername = self.filename_from_foldername(
                    possible_series_foldernames, basename(path_from_filename))
                relpath_from_foldername = pjoin(
                    basename(self.dest_dirpath), filename_from_foldername)
                path_from_foldername = pjoin(self.dest_dirpath, filename_from_foldername)

            if not path_from_foldername or (path_from_filename == path_from_foldername):
                mutual[path] = path_from_filename
            else:
                multiple[path] = {
                    'path_from_filename': path_from_filename,
                    'path_from_foldername': path_from_foldername,
                    'relpath_from_filename': relpath_from_filename,
                    'relpath_from_foldername': relpath_from_foldername
                }

        mutual_output_paths = [v for k, v in mutual.items()]
        mutual_output_paths.sort()

        ##### USER DECIDES BETWEEN RESULTS
        print
        print 'Path: %s' % (self.dest_dirpath)
        print
        if not multiple:
            # the two methods produced the same results. Print them, ask y/n
            for p in mutual_output_paths:
                print p
            print
            question = "Use these filenames or enter new term to remove"
            options = ["filenames", CANCEL]

        # the two methods produced differing results.
        # Print only the differences,  ask 1/2/n
        else:
            print 'Mutual:'
            for p in mutual_output_paths:
                print p
            print ' === '
            print 'Different:'
            multiple_keys = multiple.keys()
            multiple_keys.sort()
            for k in multiple_keys:
                print bold('%s\t|\t%s') % (multiple[k]['relpath_from_filename'],
                                           multiple[k]['relpath_from_foldername'])

            question = ' '.join([
                'Filename-based and Foldername-based produced differences: ',
                'Select which is better, or enter new term to remove'
            ])
            options = ["filenames", "foldernames", CANCEL]

        rename_map = {}

        # Possibilities: RECALCULATE, an option, '', foo (from +foo)
        answer = self.pose_question(question, options)

        if answer == "filenames":
            rename_map = deepcopy(mutual)
            rename_map.update({p: fns['path_from_filename'] for p, fns in multiple.items()})

        elif answer == "foldernames":
            rename_map = deepcopy(mutual)
            rename_map.update({p: fns['path_from_foldername'] for p, fns in multiple.items()})
        elif answer == RECALCULATE:
            return RECALCULATE
        elif answer and len(orig_paths) == 1:
            ## TODO: Re-attach file ext (and maybe checksum) if not supplied
            print 'You ignored our suggestion; supplying: %r' % (answer,)
            result = pjoin(self.dest_folder, self.dest_dirpath, answer)
            print 'Result: %r' % (result,)
            rename_map = {orig_paths[0]: result}

        elif answer and len(orig_paths) > 1:
            # more than one file
            print "We don't currently support manual mmvs :("
            return
        else:
            print 'cancelled ...'
            return

        return rename_map

    def build_command_bundle(self, content_details, rename_map):
        #pylint: disable=too-many-locals
        # To avoid completely rewriting this ...
        content_abspath = content_details['content_abspath']
        num_discarded_files = content_details['num_discarded_files']
        orig_foldername = content_details['orig_foldername']
        orig_intermeds = content_details['orig_intermeds']
        orig_filenames = content_details['orig_filenames']
        orig_paths = content_details['orig_paths']

        ##### LET'S BUILD SOME COMMANDS!
        commands = []

        self.expected_dirs.append(self.dest_dirpath)

        commands.extend(['mkdir -p "%s"' % (self.dest_dirpath,)])

        rename_map_keys = sorted(rename_map.keys())
        commands.extend(['mv -nv "%s" "%s"' % (k, rename_map[k]) for k in rename_map_keys])

        torrentfile = tfile_from_filename(content_abspath, get_torrentfilesdir(self.global_conf))

        question = 'Should these be seeded?'
        if torrentfile:
            question = 'Seed using {f}?'.format(f=torrentfile)
        do_seed = optionator(question, ['yes', 'no', CANCEL])

        seeddir_paths = {}
        if do_seed == "":  # this means CANCEL
            return
        elif do_seed == "yes":
            if not torrentfile:
                torrentfile = self.old_find_torrentfile(content_abspath)

            torrentfile_commands = self.build_torrentfile_commands(
                torrentfile, content_abspath, orig_foldername, orig_paths, rename_map,
                orig_intermeds, orig_filenames)
            commands.extend(torrentfile_commands)
        else:
            # delete remainder of files in torrentdir
            # Don't delete the arg dir if it's the same as the target dir
            # (renaming files in-place)
            dud_files_remaining = num_discarded_files > 0
            only_ever_one_file_in_dir = (os.path.isdir(content_abspath) and len(orig_paths) == 1)

            if isdir(content_abspath):
                num_remaining_files = (len(listdir(content_abspath)) - len(orig_paths))
                dir_is_now_empty = (num_remaining_files == 0)
            else:
                dir_is_now_empty = False

            # delete the source if there are remaining dud files / the dir is empty,
            # provided that it's not also the dest
            if ((dud_files_remaining or only_ever_one_file_in_dir or dir_is_now_empty) and
                (realpath(content_abspath) != realpath(self.dest_dirpath))):

                if dir_is_now_empty:
                    commands.append('rmdir "%s"' % (content_abspath,))
                else:
                    # have taken wanted files, delete remaining dir
                    commands.append('echo "Files still in the folder"')
                    commands.append('ls -aR "%s/"' % (content_abspath,))
                    commands.append('rm -Irv "%s"' % (content_abspath,))

        # a command bundle
        return {
            'commands': commands,
            'symlinks': [seeddir_paths_ for _orig_path, seeddir_paths_ in seeddir_paths.items()],
            'torrentfile': torrentfile,
            'commands_run': []
        }

    def build_torrentfile_commands(self, torrentfile, content_abspath, orig_foldername, orig_paths,
                                   rename_map, orig_intermeds, orig_filenames):
        #pylint: disable=too-many-arguments
        commands = []

        if orig_foldername:
            commands.append('mv -nv "%s" "%s"' % (content_abspath, self.global_conf['seeddir']))

        # TODO: this should be a src -> dst dict
        # TODO: this should be inside the rename_map
        seeddir_paths = {
            orig_path: pjoin(self.global_conf['seeddir'], orig_foldername, intermeds, filename)
            for orig_path, intermeds, filename in zip(orig_paths, orig_intermeds, orig_filenames)
        }
        seeddir_paths_keys = sorted(seeddir_paths.keys())

        commands.extend([
            'ln -s "%s" "%s"' % (rename_map[orig_path], seeddir_paths[orig_path])
            for orig_path in seeddir_paths_keys
        ])

        if torrentfile:
            print 'Using torrentfile %r' % (torrentfile,)
            # move torrentfile to seeddir
            commands.append('mv -nv "%s" "%s"' % (pjoin(
                get_torrentfilesdir(self.global_conf), torrentfile),
                                                  self.global_conf['seedtorrentfilesdir']))

        return commands


def check_result(command_bundle, failed):

    broken_syms = [s for s in command_bundle.get('symlinks', []) if not pexists(s)]

    if failed or broken_syms:
        print "Broken symlinks - fix them then start the torrentfile"
        print
        for b in broken_syms:
            print "Broken: \t", b

        print
        print 'Commands: (those run are #-prefixed)'
        for command in command_bundle['commands']:
            if command in command_bundle['commands_run']:
                print '# %s' % (command,)
            else:
                print command

        return False
    return True
