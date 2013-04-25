#!/usr/bin/env python

import os
from os import listdir
from os.path import expanduser, isdir, realpath
from os.path import exists as pexists
from os.path import join as pjoin

from difflib import SequenceMatcher

from debugprinter import debugprinter
from filenamer import filenamer
from retorrentlib.confparse import find_removelist, parse_divider_symbols, parse_fileext_details, parse_retorrentconf
from logdecorators.tracelogdecorator import tracelogdecorator
from optionator import optionator, eqoptionator
from os_utils.os_utils import enough_space, mkdir_p, myglob, str2utf8

class retorrenter:

    def __init__(self, configdir='', debug=False):
        self.configdir = configdir

        self.debug = debug
        self.debugprinter = debugprinter(self.debug)

    def debugprint(self,str,listol=[]):
        self.debugprinter.debugprint(str,listol)

    def reset_env(self):
        # The category folder (movies, tv ... )
        self.dest_category = ''
        self.dest_folder = ''
        self.dest_series_folder=''
        # The series or movie-name folder
        self.dest_dirpath = ''

        self.filenamer = filenamer(self.divider_symbols,
                                   self.filetypes_of_interest,
                                   the_debugprinter=self.debugprinter)

    def handle_args(self, arguments):
        content = []
        for a in arguments:
            if pexists(a):
                content.append(a)
            else:
                paths = myglob(a)
                content.extend([ p for p in paths if pexists(p) ])

        content.sort()
        if not content:
            print 'No content found'
            return

        self.global_conf, self.categories = parse_retorrentconf( self.configdir)
        self.filetypes_of_interest = parse_fileext_details(self.configdir)
        self.divider_symbols = parse_divider_symbols(self.configdir)
        self.removelist_path = find_removelist(self.configdir)

        self.commands = []
        for c in content:
            # TODO: Could really do with removing this ...
            self.reset_env()

            commandset = self.handle_content(c)
            if commandset:
                self.commands.append(commandset)

        return self.commands

    def handle_content(self, content):
        print "|\n|\n|\n|"

        the_path = os.path.abspath(content)

        # get a list of files to keep
        # NOTE: These are only those of the interesting files
        orig_paths,orig_foldername,orig_intermeds,orig_filenames,num_discarded_files = self.find_files_to_keep(the_path)

        num_interesting_files = len(orig_paths)
        self.filenamer.set_num_interesting_files(num_interesting_files)

        if len(orig_paths) == 0:
            print "No interesting files found! Skipping!"
            return

        self.debugprint("Dirpath before autoset: " + self.dest_dirpath)

        possible_series_foldernames = [
                self.filenamer.convert_filename(orig_filenames[0],True),
                self.filenamer.convert_filename(orig_foldername,True) ]

        possible_series_foldernames = [ i for i in possible_series_foldernames
                if not i == '' ]

        self.autoset_dest_dirpath(possible_series_foldernames,orig_paths)

        self.debugprint('DestFolder after autoset: ' + self.dest_folder)
        self.debugprint("Dirpath after autoset: " + self.dest_dirpath)

        if self.dest_category == "":
            self.manually_set_dest_category(content, orig_paths)

            # TODO: Remove this.
            # All circumstances where s.d_c=='' should be caught instead.
            if self.dest_category == '':
                # we are skipping this file.
                print "skipping!"
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

        if self.categories[self.dest_category]['should_rename']:
            self.debugprint('About to generate dest_dirpath; '+self.dest_dirpath)
            if self.dest_dirpath == "":
                self.manually_set_dest_dirpath(num_interesting_files,
                        possible_series_foldernames)
                if self.dest_dirpath == "":
                    print "Didn't set a directory - failing"
                    return

            # At this point, self.dest_dirpath contains the full folder path
            self.debugprint('Final dest_dirpath=' +self.dest_dirpath)
            ##################################
            ## Now to rename the filenames
            ##################################
            # create output paths based on the filenames
            dest_filenames_from_files = [ self.filenamer.convert_filename(
                    os.path.basename(file),False) for file in orig_paths]
            dest_paths_from_files = [ pjoin(self.dest_dirpath,filename)
                    for filename in dest_filenames_from_files ]

            self.debugprint('',[['dest_filenames_from_files',dest_filenames_from_files],['dest_paths_from_files',dest_paths_from_files]])

            # create output paths based on the folder name (only if given a folder)
            if os.path.isdir(the_path):

                if len(possible_series_foldernames) > 1:
                    series_foldername_from_orig_foldername = possible_series_foldernames[1]
                # there is no good series foldername. Base off the first filename.
                elif len(possible_series_foldernames) > 0:
                    series_foldername_from_orig_foldername = possible_series_foldernames[0]
                else:
                    possible_series_foldernames = ['']
                    series_foldername_from_orig_foldername = ''


                dest_filenames_based_on_folder = [
                        self.filenamer.gen_final_filename_from_foldername(
                        series_foldername_from_orig_foldername, afile)
                        for afile in dest_filenames_from_files ]

                dest_paths_from_folder = [ pjoin(self.dest_dirpath,file)
                        for file in dest_filenames_based_on_folder ]

                self.debugprint('',[['dest_filenames_from_folder',dest_filenames_based_on_folder],['dest_paths_from_folder',dest_paths_from_folder]])

            else:
                # If not given a folder, set to the same as the filename-based output.
                dest_filenames_based_on_folder = dest_filenames_from_files
                dest_paths_from_folder = dest_paths_from_files


            # list the differences between the two methods
            list_diff = []
            list_same = []
            for file_item in dest_paths_from_files:
                if not file_item in dest_paths_from_folder:
                    list_diff += [(file_item,dest_paths_from_folder[dest_paths_from_files.index(file_item)])]
                else:
                    list_same += [(file_item,dest_paths_from_folder[dest_paths_from_files.index(file_item)])]

            # prepare the lists for printing, then sort.
            # Can't sort the orig and dest lists, as they may sort differently
            printable_dest_paths_from_files = [ i for i in dest_paths_from_files ]
            printable_list_diff_file_based = [ i[0] for i in list_diff ]
            printable_list_diff_folder_based = [ i[1] for i in list_diff ]
            printable_list_same = [ i[0] for i in list_same ]

            printable_dest_paths_from_files.sort()
            printable_list_diff_file_based.sort()
            printable_list_diff_folder_based.sort()
            printable_list_same.sort()

            ##### USER DECIDES BETWEEN RESULTS

            # the two methods produced the same results. Print one, ask y/n
            print
            if len(list_diff) == 0:
                for i in printable_dest_paths_from_files:
                    print i

                question = "Use these filenames or enter new term to remove"
                options = ["filenames", "cancel"]

            # the two methods produced different results. (either complete or partial)
            # Print only the differences,  ask 1/2/n
            else:
                if len(printable_list_same) > 0:
                    print "The Same:"
                    for file in printable_list_same:
                        print "\t", file
                print "File-based:"
                for file_based in printable_list_diff_file_based:
                    print "\t", file_based
                print "Folder-based:"
                for folder_based in printable_list_diff_folder_based:
                    print "\t", folder_based

                question = "Filename-based and Foldername-based produced differences: Select which is better, or enter new term to remove"
                options = ["filenames", "foldernames", "cancel"]

            print

            # Possibilities: '-', an option, '', foo (from +foo)
            answer = self.pose_question(question,options)

            if answer == '-':
                return self.handle_content(content)
            elif answer  == "cancel":
                return
            elif answer == "filenames":
                dest_paths = dest_paths_from_files
            elif answer == "foldernames":
                dest_paths = dest_paths_from_folder
            elif num_interesting_files == 1:
                ## TODO: Re-attach file ext if ignored

                print 'You ignored our suggestion; taking: "' + answer + '"'
                dest_paths = [ pjoin(self.dest_folder,
                        self.dest_dirpath,answer) ]
            else:
                # more than one file
                print "We don't currently support manual mmvs :("
                return self.handle_content(content)

        else:
            print "Not renaming files"
            self.dest_dirpath = pjoin(self.dest_folder,orig_foldername)
            dest_paths = [ pjoin(self.dest_dirpath,filename) for filename in orig_filenames ]

        ##### LET'S BUILD SOME COMMANDS!
        commands = []
        torrentfile = ""

        # make the dir immediately, for the case show*avi
        mkdir_p(self.dest_dirpath)

        for dest in dest_paths:
            if os.path.exists(dest):
                print 'Already exists, not moving: ', dest

        commands += [ "mv -nv " + '"' + orig + '"' + " " + '"'+dest+'"' for (orig,dest) in zip(orig_paths,dest_paths) ]

        do_seed = optionator("Should these be seeded?" , ['yes', 'no' , '<cancel>'] )
        torrentfile = ''
        seeddir_paths = []
        # this means '<cancel>'
        if do_seed == "":
            return
        elif do_seed  == "yes" :
            # link arg to .torrent via optionator
            torrentfile = self.find_torrentfile(the_path)

            if not orig_foldername == "":
                commands.append('mv -nv "%s" "%s"' % (the_path, self.global_conf['seeddir']))

            if not torrentfile == '':
                # move torrentfile to seeddir
                commands.append('mv -nv "%s" "%s"' % (
                                  pjoin(self.global_conf['torrentfilesdir'], torrentfile),
                                  self.global_conf['seedtorrentfilesdir']))

            # gen filenames + foldername for symlinked files
            seeddir_paths = self.gen_seeddir_paths(orig_foldername,
                                                   orig_intermeds,
                                                   orig_filenames)

            commands += [ "ln -s " + '"'+dest+'"' + " " + '"'+seedpath+'"'
                            for dest,seedpath in zip(dest_paths,seeddir_paths) ]
        else:

            # delete remainder of files in torrentdir
            # Don't delete the arg dir if it's the same as the target dir (renaming files in-place)
            dud_files_remaining = num_discarded_files > 0
            only_ever_one_file_in_dir = os.path.isdir(content) and num_interesting_files == 1
            dir_is_now_empty = isdir(content) and len(listdir(content)) - num_interesting_files == 0

            # delete the source if there are remaining dud files / the dir is empty, provided that it's not also the dest
            if ((dud_files_remaining or only_ever_one_file_in_dir or dir_is_now_empty)
                    and not realpath(content) == realpath(self.dest_dirpath)):

                if dir_is_now_empty:
                    commands += [ 'rmdir "' + the_path + '"' ]
                else:
                    # have taken wanted files, delete remaining dir
                    the_path = '"' + the_path + '"'

                    commands += [ 'echo "Files still in the folder" ' ]
                    commands += [ 'ls -aR ' + the_path + '/']
                    commands += [ "rm -Irv " + the_path ]

        return { 'commands': commands, 'symlinks': seeddir_paths, 'torrentfile': torrentfile}

    def set_num_interesting_files(self,num_interesting_files):
        self.filenamer.set_num_interesting_files(num_interesting_files)

    def check_symlinks(self, seeddir_paths):

        # check any symlinks that were created
        broken_syms = []
        for seedpath in seeddir_paths:
            if not os.path.exists(seedpath):
                broken_syms += [seedpath]

        if len(broken_syms) > 0 :
            return { 'success': False, 'broken': broken_syms }

        # We have moved the files, but are not seeding. Return an empty string.
        return { 'success': True }


    def autoset_dest_dirpath(self,possible_series_foldernames,orig_paths):
        """
        dest_dirpath is the 'series name' or similar folder inside the
            category folder
        """

        self.debugprint('retorrenter.autoset_dest_dirpath(' + ','.join(possible_series_foldernames)+')')

        if self.dest_category:
            # the dest category is already set from somewhere else
            categories = [ (self.dest_category,
                            self.categories[self.dest_category]) ]
        else:
            categories = self.categories.items()

        for category, details in categories:
            for cat_folder in details['content_paths']:
                for poss_series_folder in possible_series_foldernames:
                    possible_path = expanduser(pjoin(cat_folder, poss_series_folder))
                    self.debugprint('Looking for ' + possible_path)
                    if os.path.exists(possible_path):
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
                possible_path = pjoin(cat_folder,self.dest_series_folder)

                self.debugprint('Checking:' + possible_path)
                self.debugprint('Equivalent candidate: ' + possible_path)

                if (os.path.exists(possible_path) and
                        enough_space(orig_paths, possible_path)):
                    self.debugprint('Equivalent candidate exists already and has enough space: ' + possible_path)

                    self.dest_folder = cat_folder
                    self.dest_dirpath = possible_path
                    return

            for cat_folder in self.dest_category_paths():
                self.debugprint('Equivalent candidate has enough space: ' + possible_path)
                possible_path = pjoin(cat_folder,self.dest_series_folder)

                if enough_space(orig_paths, possible_path):
                    self.dest_folder = cat_folder
                    self.dest_dirpath = possible_path
                    return

            # There are no drives in the list with enough disk space ... :(
            # TODO: Bail here.

        else:
            # we don't have enough info to make the dir on a different drive
            pass


    def manually_set_dest_category(self, argument, orig_paths):
        question = "Destination for " + argument
        dest_category_name = optionator(question, self.categories.keys() + ["<cancel>"] )

        if dest_category_name in self.categories:
            self.dest_category = dest_category_name
            self.autoset_dest_folder_from_dest_category(orig_paths)
            return

        # XXX
        print dest_category_name
        if dest_category_name == '<cancel>':
            raise
        else:
            print 'Error -- category was unrecognised!'
            self.manually_set_dest_category(argument,orig_paths)

    @tracelogdecorator
    def autoset_dest_folder_from_dest_category(self,orig_paths):
        if self.dest_category:
            for path in self.categories[self.dest_category]['content_paths']:
                self.debugprint('Possible path: ' + path)
                if not os.path.exists(path):
                    print "Warning: Config contains a path that doesn't exist: %s"%(
                                path,)
                elif enough_space(orig_paths,path):
                    self.debugprint('Setting dest_folder to: '+path)
                    self.dest_folder = path
                    return

    def manually_set_dest_dirpath(self,num_interesting_files,
            possible_series_foldernames):

        self.debugprint('retorrenter.manually_set_dest_dirpath()')
        # gen dest paths from these foldernames

        # if a movie has +1 files, need a folder. All else might need a folder
        if self.is_movie() and num_interesting_files == 1:
            self.debugprint('manually_set_dest_dirpath: This is a movie, no need for a folder')
            self.dest_dirpath = self.dest_folder
        else:

            if self.is_movie() or num_interesting_files > 1:
                dirpath_q = "What foldername should we use?"
                dirpath_q_opts = possible_series_foldernames
            else:
                dirpath_q =    "Is this a series? If so, use what folder name?"
                dirpath_q_opts = possible_series_foldernames + [ "" ]

            dirpath_ans = self.pose_question(dirpath_q, dirpath_q_opts)

            if not dirpath_ans == '-':
                self.dest_dirpath = pjoin(self.dest_folder,dirpath_ans)
            else:
                # a new removeitem has been added - regenerate psf

                possible_series_foldernames = [
                    self.filenamer.convert_filename(item,True)
                    for item in possible_series_foldernames ]

                self.manually_set_dest_dirpath(num_interesting_files,
                        possible_series_foldernames)
                return

    # Note: returns '-' if a recurse is needed
    def pose_question(self,question,options):

        answer = eqoptionator(question,options)

        if answer in options or answer == '':
            return answer
        elif answer.startswith('+'):
            return answer[1:]
        elif answer.startswith('-'):
            self.filenamer.add_to_removelist(answer[1:])
            return '-'
        else:
            self.filenamer.tmp_remove_list.append(answer)
            return '-'

    # For all files
    # Needs to return:
    #    Foldername (if arg is torrent/$FOLDER )
    #        orig_foldername neither begins nor ends with slashes
    #    Intermediate ( torrent/$FOLDER/$INTERMED/ )
    #        elements of orig_intermeds elements have neither beginning nor ending slashes
    #    Files ( torrent.$FOLDER/$INTERMED/$FILE )
    def find_files_to_keep(self,the_path):
        file_paths = []
        file_names = []
        intermeds = []
        # if (folder), figure out which files are the movie
        if os.path.isdir(the_path):

            orig_foldername = os.path.basename(the_path)

            for (path,dirs,files) in os.walk(the_path):
                for file in files:
                    file_path = path + "/" + file
                    thisfile_intermed = path[len(the_path)+1:]
                    if os.path.exists(file_path) :
                        file_paths += [os.path.abspath(file_path)]
                        file_names += [os.path.basename(file_path)]
                        intermeds += [thisfile_intermed]
                    else:
                        print "Internal error - built a path, then file didn't exist(?)"
        else:
            orig_foldername = "" # it's a file, flat in ~/torrents
            if os.path.exists(the_path):
                file_path = the_path
                file_paths = [os.path.abspath(file_path)]
                file_names = [os.path.basename(file_path)]
                intermeds = [""]*len(file_names)

        # remove files that aren't of interest
        filepaths_to_keep,intermeds_to_keep,filenames_to_keep,num_discarded_files = self.get_movies_and_extras(file_paths,intermeds,file_names)

        return filepaths_to_keep,orig_foldername,intermeds_to_keep,filenames_to_keep, num_discarded_files


    # strip uninteresting files from the lists
    def get_movies_and_extras(self,list_of_filepaths, list_of_intermeds, list_of_filenames):

        filepaths_to_keep = []
        intermeds_to_keep = []
        filenames_to_keep = []
        num_discarded_files = 0

        for filepath,intermed,filename in zip(list_of_filepaths,list_of_intermeds, list_of_filenames):
            if self.is_of_interest(filepath,filename):
                filepaths_to_keep += [filepath]
                intermeds_to_keep += [intermed]
                filenames_to_keep += [filename]
            else:
                #print "Skipping ",os.path.basename(filepath)
                num_discarded_files += 1

        return filepaths_to_keep,intermeds_to_keep,filenames_to_keep,num_discarded_files

    @tracelogdecorator
    def is_of_interest(self,file_path, filename):

        (path,extension) = os.path.splitext(file_path)
        # trim the . from the extension for matching
        extension = extension[1:].lower()

        for foi in self.filetypes_of_interest:
            if extension == foi['fileext']:
                # if the filename has something which excludes it, skip it
                # eg. 'sample'
                for exclude in foi['ignore_if_in_filename']:
                    if exclude == '':
                        continue
                    if not filename.lower().find(exclude.lower()) == -1:
                        # this file has a phrase which excludes it
                        self.debugprint(filename + ' contains a phrase which excludes it')
                        return False
                filestat = os.stat(file_path)
                # this will actually get the size of all the blocks, not the space used.
                # Close enough ... :P
                disk_filesize_kB = filestat.st_blocks*filestat.st_blksize/(8*1024)

                if disk_filesize_kB > foi['goodsize']:
                    return True
                else:
                    self.debugprint('Size:' + str(disk_filesize_kB) +  'kB <' + str(foi['goodsize']) +'kB for:' + file_path)
        self.debugprint(filename + " didn't trigger any interest ...")
        return False

    def is_movie(self):
        if self.dest_category:
            return self.categories[self.dest_category]['treat_as'] == 'movies'
        return False

    # TODO: episoder _must_ be able to return the epno - *use this*.
    def find_torrentfile(self, the_path):
        # get the file / foldername (not necc. the same as the arg itself
        split_path = the_path.rsplit('/')
        arg_name = split_path[-1]

        the_torrentfiles =  os.listdir(self.global_conf['torrentfilesdir'])
        exclude = [ c['torrentfile'] for c in self.commands ]

        tfiles = []
        for tfile in the_torrentfiles:
            if tfile in exclude:
                continue
            cf = self.filenamer.convert_filename(
                        tfile.rstrip('torrent').rstrip('.'),
                        True,
                        interactive=False)

            score = SequenceMatcher('',
                                    str2utf8(arg_name),
                                    str2utf8(cf)).ratio()

            tfiles += [{'filename':tfile, 'conv_filename':cf, 'score':score } ]


        tfiles = sorted(tfiles, self.compare_scored_tfiles)

        chosen_torrentfile = optionator('For: '+arg_name,
                                        [t['filename'] for t in tfiles])

        return chosen_torrentfile

    def compare_scored_tfiles(self, A, B):
        cmp_ = cmp(B['score'],A['score'])

        if not cmp_ == 0:
            return cmp_
        return cmp(A['filename'], B['filename'])

    def gen_seeddir_paths(self,orig_foldername,orig_intermeds,orig_filenames):

        return [ pjoin(self.global_conf['seeddir'], orig_foldername, intermeds, filename)
               for intermeds, filename in zip(orig_intermeds, orig_filenames) ]
