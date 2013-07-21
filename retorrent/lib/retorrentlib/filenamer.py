#!/usr/bin/ipython

from os.path import dirname
from os.path import join as pjoin


from braced import extract_checksum, is_checksum, remove_braces
from debugprinter import debugprinter
from episoder import episoder
from retorrentlib import removeset
from retorrentlib.restring import dotjoin, endot, remove_camelcase, remove_zwsp
from retorrentlib.relist import lowercase_non_checksums, remove_nonfinal_elements_if_in_set

class filenamer:
    def __init__(self, divider_list, filetypes_of_interest,
                 the_debugprinter=debugprinter(False)):

        self.remove_set = removeset.read_from_file()
        self.tmp_remove_set = set()

        self.divider_list = divider_list
        self.fileext_list = [ f['fileext'] for f in filetypes_of_interest ]

        self.the_episoder = episoder()
        self.debugprinter = the_debugprinter

        self.is_movie = False

    def debugprint(self, str, listol=[]):
        self.debugprinter.debugprint(str,listol)

    def add_to_removeset(self, item):
        self.remove_set = removeset.add_and_sync(self.remove_set, item)

    def add_to_tmp_removeset(self, item):
        self.tmp_remove_set.add(item)

    def set_num_interesting_files(self,num_interesting_files):
        self.the_episoder.set_num_interesting_files(num_interesting_files)

    def set_movie(self, is_movie):
        self.is_movie = is_movie
        self.the_episoder.set_movie(is_movie)

    def convert_filename(self, filename, is_foldername, interactive=True):
        self.the_episoder.interactive = interactive

        if filename == '':
            self.debugprint('Not converting blank filename!',[])
            return ''
        self.debugprint('filenamer.convert_filename(' + filename + ', is_foldername==' + str(is_foldername) + ')')

        filename = self.remove_divider_symbols(filename)

        self.debugprint('filenamer.convert_filename, after self.remove_divider_symbols : ' + filename )

        # remove braces from anything that isn't a checksum or a year
        filename = remove_braces(filename, preserve_checksum=not is_foldername)

        self.debugprint('filenamer.convert_filename, after self.sort_out_braces: ' + filename )

        # Apparently, there are things called 'zero width spaces'. Remove them.
        filename = remove_zwsp(filename)
        self.debugprint('filenamer.convert_filename, after remove_zwsp: ' + filename )

        # change CamelCase to Camel.Case
        filename = remove_camelcase(filename)

        self.debugprint('filenamer.convert_filename, after remove_camelcase: ' + filename )

        filename = endot(filename)

        self.debugprint('filenamer.convert_filename, after endot: ' + filename )

        filename_split = filename.split('.')
        filename_split = lowercase_non_checksums(filename_split)

        self.debugprint('filenamer.convert_filename, after filenamer.lowercase_non_checksums: ' + '[' + ', '.join(filename_split) + ']')

        if not is_foldername:
            # this is a filename ending in a file extension -- preserve the extension
            filename_split = remove_nonfinal_elements_if_in_set(filename_split,
                                                        self.remove_set | self.tmp_remove_set)

        else:
            # may prune the final element if it's in the removeset
            filename_split = [ elem for elem in filename_split
                               if not elem in self.remove_set | self.tmp_remove_set ]


        # Detect and Convert episode numbers.
        # NEW! Movies have cd01,cd02-so they go through episoder
        filename_split,epno_index = self.the_episoder.add_series_episode_details(filename_split,is_foldername)

        self.debugprint('filenamer.convert_filename, after episoder.add_series_episode_details: ' + '[' + ', '.join(filename_split) + ']')

        if is_foldername:

            # don't want file extensions in a folder name
            if filename_split[-1] in self.fileext_list:
                filename_split = filename_split[:-1]

            self.debugprint('filenamer.convert_filename, creating a folder name, so : after filenamer.remove_elements_based_on_list(file_extensions): ' + '[' + ', '.join(filename_split) + ']')

        if not self.is_movie:
            filename_split = self.remove_following_text(filename_split, epno_index, is_foldername)
            self.debugprint('filenamer.convert_filename, not a movie (no episode number) so: after filenamer.remove_following_text: ' + '[' + ', '.join(filename_split) + ']')

        filename = dotjoin(*filename_split)

        self.debugprint('filenamer.convert_filename RETURNING:' + filename)
        return filename

    def gen_final_filename_from_foldername(self, the_dirpath, filename):
        """
        Replace the title in the filename passed with that passed as the folder name

        # get TITLE from foldername
        # get EPNO,FILEEXT from filename  // What about the checksum?
        # Make: TITLE.EPNO.FILEEXT
        """
        self.debugprint('filenamer.gen_final_filename_from_foldername(the_dirpath=%r, filename=%r)' % (the_dirpath, filename))

        title = self.convert_filename(the_dirpath, is_foldername=True)

        # GET EPNO from filename
        # run convert_filename on filename as a filename. Then pull epno
        generated_filename = self.convert_filename(filename, is_foldername=False)
        epno = self.the_episoder.get_good_epno(filename)

        checksum = extract_checksum(filename)
        # TODO: preserve year if in filename

        fileext = self.find_fileext(filename)

        self.debugprint('filenamer.gen_final_filename_from_foldername:')
        self.debugprint('Given filename={filename}, generated_filename={generated_filename}, title={title}, epno={epno}, checksum={checksum}, fileext={fileext}'.format(filename=filename, generated_filename=generated_filename, title=title, epno=epno, checksum=checksum, fileext=fileext))

        # join. We've lost the file ext ...
        filename_out = dotjoin(title, epno, checksum, fileext)

        output = pjoin(dirname(the_dirpath.strip('/')),filename_out)

        return output

    def remove_divider_symbols(self, filename):
        for symbol in self.divider_list:
            if symbol in filename:
                filename = filename.replace(symbol,".")
        return filename

    # does this list contain '.mkv' or 'mkv' ?
    def is_fileext(self, item):
        return item in self.fileext_list

    def find_fileext(self, filename):
        f = filename.split('.')
        f.reverse()
        for i in f:
            if self.is_fileext(i):
                return i
        return ''

    def remove_following_text(self, filename_split, epno_index, is_foldername):
        """
        removes the text following the epno_index except for checksums and the file extension
        """
        # there is no epno in this filename
        if epno_index == -1:
            return filename_split

        if not is_foldername:
            epno_index += 1

        self.debugprint('filenamer.remove_following_text(' + str(filename_split) + ',' + str(epno_index) + ')')

        rmlist = []
        for index,elem in enumerate(filename_split[epno_index:]):
            if not is_checksum(elem) and not self.is_fileext(elem):
                rmlist += [index+epno_index]

        rmlist.sort(reverse=True)

        for i in rmlist:
            del filename_split[i]

        return filename_split


if __name__ == '__main__':
    import doctest
    doctest.testmod()
