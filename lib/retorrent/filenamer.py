""" retorrent.filenamer """
from os.path import dirname
from os.path import join as pjoin

from redecorators import tracelogdecorator

from . import confparse, removeset
from .braced import extract_checksum, is_checksum, remove_braces
from .episoder import Episoder
from .restring import dotjoin, endot, remove_camelcase, remove_zwsp
from .relist import lowercase_non_checksums


class Filenamer(object):

    def __init__(self, divider_list, filetype_definitions):

        # items to be filtered out of the pre-tokenized filename
        self.pretokenized_removeset = removeset.read_from_file(
            confparse.find_pretokenized_removelist())

        # items to be removed from the tokenized filename
        self.removeset = removeset.read_from_file(confparse.find_removelist())
        self.tmp_removeset = set()

        self.divider_list = divider_list
        self.fileext_list = [fileext for fileext in filetype_definitions]

        self.the_episoder = Episoder()

        self.is_movie = False

    def add_to_removeset(self, item):
        self.removeset = removeset.add_and_sync(self.removeset, item)

    def add_to_tmp_removeset(self, item):
        self.tmp_removeset.add(item)

    def set_num_interesting_files(self, num_interesting_files):
        self.the_episoder.set_num_interesting_files(num_interesting_files)

    def set_movie(self, is_movie):
        self.is_movie = is_movie
        self.the_episoder.set_movie(is_movie)

    @tracelogdecorator
    def convert_filename(self, filename, is_foldername, interactive=True):
        self.the_episoder.interactive = interactive

        if filename == '':
            return ''

        for remove in self.pretokenized_removeset:
            filename = filename.replace(remove, '')

        filename = self.remove_divider_symbols(filename)

        # remove braces from anything that isn't a checksum or a year
        filename = remove_braces(filename,
                                 preserve_checksum=not is_foldername,
                                 interactive=interactive)

        # Apparently, there are things called 'zero width spaces'. Remove them.
        filename = remove_zwsp(filename)

        # change CamelCase to Camel.Case
        filename = remove_camelcase(filename)

        filename = endot(filename)

        filename_split = filename.split('.')
        filename_split = lowercase_non_checksums(filename_split)

        full_removeset = self.removeset.union(self.tmp_removeset)

        filename_split = self.apply_removeset(filename_split, full_removeset, is_foldername)

        # Detect and convert episode numbers.
        filename_split, epno_index = self.the_episoder.add_series_episode_details(filename_split)

        if is_foldername:
            # don't want file extensions in a folder name
            if filename_split[-1] in self.fileext_list:
                filename_split = filename_split[:-1]

        if not self.is_movie:
            filename_split = self.remove_following_text(filename_split, epno_index, is_foldername)

        filename = dotjoin(*filename_split)

        return filename

    @tracelogdecorator
    def gen_final_filename_from_foldername(self, the_dirpath, filename):
        """
        Replace the title in the filename passed with that passed as the folder name

        # get TITLE from foldername
        # get EPNO,FILEEXT from filename  // What about the checksum?
        # Make: TITLE.EPNO.FILEEXT
        """
        title = self.convert_filename(the_dirpath, is_foldername=True)

        # GET EPNO from filename
        # run convert_filename on filename as a filename. Then pull epno
        generated_filename = self.convert_filename(filename, is_foldername=False)
        epno = self.the_episoder.get_good_epno(generated_filename)

        checksum = extract_checksum(filename)
        # TODO: preserve year if in filename

        fileext = self.find_fileext(filename)

        # join. We've lost the file ext ...
        filename_out = dotjoin(title, epno, checksum, fileext)

        output = pjoin(dirname(the_dirpath.strip('/')), filename_out)

        return output

    @tracelogdecorator
    def remove_divider_symbols(self, filename):
        for symbol in self.divider_list:
            if symbol in filename:
                filename = filename.replace(symbol, ".")
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

    @staticmethod
    @tracelogdecorator
    def apply_removeset(filename_split, full_removeset, is_foldername):
        final_element = filename_split[-1]
        filename_split = [elem for elem in filename_split[0:-1] if not elem in full_removeset]
        if not is_foldername:
            # this is a filename ending in a file extension -- preserve the extension
            filename_split = filename_split + [final_element]

        else:
            if not final_element in full_removeset:
                filename_split = filename_split + [final_element]
        return filename_split

    @tracelogdecorator
    def remove_following_text(self, filename_split, epno_index, is_foldername):
        """
        removes the text following the epno_index except for checksums and the file extension
        """
        # there is no epno in this filename
        if epno_index == -1:
            return filename_split

        if not is_foldername:
            epno_index += 1

        rmlist = []
        for index, elem in enumerate(filename_split[epno_index:]):
            if not is_checksum(elem) and not self.is_fileext(elem):
                rmlist += [index + epno_index]

        rmlist.sort(reverse=True)

        for i in rmlist:
            del filename_split[i]

        return filename_split
