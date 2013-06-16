#!/usr/bin/ipython

from os.path import dirname
from os.path import join as pjoin


from braced import  extract_checksum, is_checksum, remove_braces
from debugprinter import debugprinter
from episoder import episoder
from retorrentlib import removeset
from retorrentlib.restring import dotjoin, endot, remove_camelcase, remove_zwsp
from retorrentlib.relist import remove_elements_based_on_list

class filenamer:
    def __init__(self, divider_list, filetypes_of_interest,
                 the_debugprinter=debugprinter(False)):

        self.remove_set = removeset.read_from_file()
        self.tmp_remove_set = set()

        self.divider_list = divider_list
        self.fileext_list = [ f['fileext'] for f in filetypes_of_interest ]

        self.the_episoder = episoder(the_debugprinter)
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

        # remove braces from anything that isn't a checksum
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
        filename_split = self.to_lowercase(filename_split)

        self.debugprint('filenamer.convert_filename, after filenamer.to_lowercase: ' + '[' + ', '.join(filename_split) + ']')

        filename_split = remove_elements_based_on_list(filename_split, self.remove_set)
        self.debugprint('filenamer.convert_filename, after filenamer.remove_elements_based_on_list(removeset): ' + '[' + ', '.join(filename_split) + ']')

        filename_split = remove_elements_based_on_list(filename_split, self.tmp_remove_set)

        # pre-2012 Don't want years tangling the episoder.
        # pre-2012 Doesn't work well either way, this is better than the opposite
        # 2012-03 Episoder needs to know about years, as they may have
        #                been preserved by filenamer. Therefore, episoder
        #                handles all year info now.
        #filename_split = self.remove_years(filename_split)
        #self.debugprint('filenamer.convert_filename, after episoder.remove_years: ' + '[' + ', '.join(filename_split) + ']')

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
            filename_split = self.remove_following_text(filename_split,epno_index, is_foldername)
            self.debugprint('filenamer.convert_filename, not a movie (no episode number) so: after filenamer.remove_following_text: ' + '[' + ', '.join(filename_split) + ']')

        filename_split = [ i for i in filename_split if i ]
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
        self.debugprint('filenamer.gen_final_filename_from_foldername(the_dirpath=' + the_dirpath + ', filename=' + filename + ')')

        # GET EPNO from filename
        # run convert_filename on filename as a filename. Then pull epno
        filename = self.convert_filename(filename,is_foldername=False)
        self.debugprint('converted the filename to: ',filename)
        epno = self.the_episoder.get_good_epno(filename)
        checksum = extract_checksum(filename)
        # TODO: preserve year if in filename

        fileext = self.find_fileext(filename)

        # Get Title from Foldername
        #foldername = os_utils.get_foldername(the_dirpath)
        title = self.convert_filename(the_dirpath, is_foldername=True)

        self.debugprint('filenamer.gen_final_filename_from_foldername: Got: filename=' + filename + ' epno=' +epno+ ' fileext=' + fileext)

        # join. We've lost the file ext ...
        filename_out = dotjoin(title, epno, checksum, fileext)

        output = pjoin(dirname(the_dirpath.strip('/')),filename_out)

        return output

    def to_lowercase(self, filename_split):
        # look for a checksum. Lowercase everything else
        for index,item in enumerate(filename_split):
            if not is_checksum(item):
                filename_split[index] = item.lower()
        return filename_split

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
