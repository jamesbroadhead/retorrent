#!/usr/bin/ipython

import os

import removelist

from debugprinter import debugprinter
from episoder import episoder
from logdecorators.tracelogdecorator import tracelogdecorator

hexdigits = "0123456789abcdefABCDEF"

braces = {
    '[' : ']',
    '{' : '}',
    '(' : ')'
}

class filenamer:

    def __init__(self, divider_list , filetypes_of_interest, the_debugprinter=debugprinter(False)):

        self.remove_list = removelist.read_list()
        self.tmp_remove_list = []

        self.divider_list = divider_list
        self.fileext_list = [ f['fileext'] for f in filetypes_of_interest ]

        self.the_episoder = episoder(the_debugprinter)
        self.debugprinter = the_debugprinter

        self.is_movie = False

    def debugprint(self, str, listol=[]):
        self.debugprinter.debugprint(str,listol)

    def add_to_removelist(self,item):
        self.remove_list = removelist.add_and_sync(self.remove_list,item)

    def set_num_interesting_files(self,num_interesting_files):
        self.the_episoder.set_num_interesting_files(num_interesting_files)

    def set_movie(self, is_movie):
        self.is_movie = is_movie
        self.the_episoder.set_movie(is_movie)

    def convert_filename(self, filename,is_foldername,interactive=True):
        self.the_episoder.interactive = interactive

        #if interactive:
            #print 'Examining: ' + filename
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
        filename = self.remove_zwsp(filename)

        self.debugprint('filenamer.convert_filename, after filenamer.remove_zwsp: ' + filename )

        # change CamelCase to Camel.Case
        filename = self.remove_camelcase(filename)

        self.debugprint('filenamer.convert_filename, after filenamer.remove_camelcase: ' + filename )

        filename = self.add_necc_dots(filename)

        self.debugprint('filenamer.convert_filename, after filenamer.add_necc_dots: ' + filename )

        filename_split = filename.split('.')
        filename_split = self.to_lowercase(filename_split)

        self.debugprint('filenamer.convert_filename, after filenamer.to_lowercase: ' + '[' + ', '.join(filename_split) + ']')

        filename_split = self.remove_extra_details(filename_split, self.remove_list)
        filename_split = self.remove_extra_details(filename_split, self.tmp_remove_list)

        self.debugprint('filenamer.convert_filename, after filenamer.remove_extra_details(removelist): ' + '[' + ', '.join(filename_split) + ']')

        # pre-2012 Don't want years tangling the episoder.
        # pre-2012 Doesn't work well either way, this is better                     #                than the opposite
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
            filename_split = self.remove_extra_details(filename_split,self.fileext_list)
            self.debugprint('filenamer.convert_filename, creating a folder name, so : after filenamer.remove_extra_details(file_extensions): ' + '[' + ', '.join(filename_split) + ']')

        if not self.is_movie:
            filename_split = self.remove_following_text(filename_split,epno_index, is_foldername)
            self.debugprint('filenamer.convert_filename, not a movie (no episode number) so: after filenamer.remove_following_text: ' + '[' + ', '.join(filename_split) + ']')


        # remove any empty elements from the filename
        filename_split = self.remove_empty_elements(filename_split)

        self.debugprint('filenamer.convert_filename, after filenamer.remove_empty_elements: ' + '[' + ', '.join(filename_split) + ']')

        filename = ".".join(filename_split)

        self.debugprint('filenamer.convert_filename RETURNING:' + filename)
        return filename

    # get TITLE from foldername
    # get EPNO,FILEEXT from filename
    # Make: TITLE.EPNO.FILEEXT
    def gen_final_filename_from_foldername(self,the_dirpath, filename):
        self.debugprint('filenamer.gen_final_filename_from_foldername(the_dirpath=' + the_dirpath + ', filename=' + filename + ')')

        # GET EPNO from filename
        # run convert_filename on filename as a filename. Then pull epno
        filename = self.convert_filename(filename,is_foldername=False)
        self.debugprint('converted the filename to: ',filename)
        epno = self.the_episoder.get_good_epno(filename)
        fileext = self.find_fileext(filename)

        # Get Title from Foldername
        #foldername = os_utils.get_foldername(the_dirpath)
        newfilename = self.convert_filename(the_dirpath,is_foldername=True)

        self.debugprint('filenamer.gen_final_filename_from_foldername: Got: filename=' + filename + ' epno=' +epno+ ' fileext=' + fileext)

        # join. We've lost the file ext ...
        filename_out = '.'.join((newfilename,epno,fileext))
        filename_out = self.remove_dupe_dots(filename_out)

        output = os.path.join(os.path.dirname(the_dirpath.strip('/')),filename_out)

        return output

    # removes Zero Width Spaces from a string.
    # Returns in UTF-8. HERE BE DRAGONS
    def remove_zwsp(self,filename):

        if type(filename) == type(u'unicode'):
            ufilename = filename
        else:
            ufilename = unicode(filename,'utf-8', errors='ignore')

        zwsp = u'\u200b'

        while zwsp in ufilename:
            ufilename = ufilename[0:ufilename.find(zwsp)] + ufilename[ufilename.find(zwsp)+len(zwsp):]

        #filename = ufilename.encode()

        return ufilename


    def add_necc_dots(self, filename):
        divide_items = ["["]
        for item in divide_items:
            if item in filename:
                index = filename.find(item)
                while not index == -1:
                    if not index == 0 and not filename[index-1] == ".":
                        filename = filename[0:index] + "." + filename[index:]
                    # index + 2 is the next char after the item
                    index = filename[index+2:].find(item)

        return filename

    def remove_dupe_dots(self,filename):
        filename = filename.strip('.')

        ddot_index = filename.find("..")
        while not ddot_index == -1:
            filename = filename[0:ddot_index] + filename[ddot_index+1:]
            ddot_index = filename.find("..")

        return filename

    def to_lowercase(self, filename_split):
        # look for a checksum. Lowercase everything else
        for index,item in enumerate(filename_split):
            if not is_checksum(item):
                filename_split[index] = item.lower()
        return filename_split


    def remove_empty_elements(self, filename_split):
        return [ item for item in filename_split if not item == '' ]

    def remove_divider_symbols(self, filename):
        for symbol in self.divider_list:
            if symbol in filename:
                filename = filename.replace(symbol,".")
        return filename

    def remove_camelcase(self, filename):
        if len(filename) == 0:
            return filename
        outfilename = ""
        old = filename[0]
        outfilename += old
        for curr in filename[1:]:
            if old.islower() and curr.isupper():
                outfilename += "."
            old = curr
            outfilename += curr
        return outfilename

    # this isn't the global 'remove_list', it's any list of things to remove
    def remove_extra_details(self, filename_split, remove_list):
        self.debugprint('')
        self.debugprint('Will remove any of : ' + ','.join(remove_list))
        #self.debugprint('Filename before removal: ' + ','.join(filename_split))
        fsplit = [ item for item in filename_split if not item in remove_list ]
        #self.debugprint('Filename after removal: ' + ','.join(fsplit))
        return fsplit


    # does this list contain '.mkv' or 'mkv' ?
    def is_fileext(self,item):
        return item in self.fileext_list

    def find_fileext(self,filename):
        f = filename.split('.')
        f.reverse()
        for i in f:
            if self.is_fileext(i):
                return i
        return ''

    def remove_following_text(self,filename_split,epno_index,is_foldername):

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


@tracelogdecorator
def is_checksum(item):
    """
    >>> is_checksum('88888888')
    True

    >>> is_checksum('halleo')
    False

    >>> is_checksum('8888888')
    False

    >>> is_checksum('888888888')
    False

    >>> is_checksum('[88888888]')
    True

    >>> is_checksum('(88888888)')
    True
    """
    # 8-digit checksum + braces
    if len(item) == 10:
        if not item[0] in braces or item[-1] == braces.get(item[0], None):
            return False
        item = item[1:-1]

    if not len(item) == 8:
        return False

    if set(item) <= set(hexdigits):
        return True
    return False

def remove_braces(filename, preserve_checksum=True, remove_content=True):
    """
    Removes braces and internal content, with special rules for checksums
    Optionally preserves content, removing braces

    >>> remove_braces('foo.bar.(what).zamf', remove_content=False)
    'foo.bar.what.zamf'

    >>> remove_braces('foo.bar.(what).zamf', remove_content=True)
    'foo.bar.zamf'

    >>> remove_braces('foo.bar.(w(h)at).zamf', remove_content=False)
    'foo.bar.w.h.at.zamf'

    >>> remove_braces('foo.bar.(w(h)at).zamf', remove_content=True)
    'foo.bar.zamf'

    >>> remove_braces('foo.bar.what.(88888888).zamf', remove_content=False)
    'foo.bar.what.[88888888].zamf'

    >>> remove_braces('foo.bar.what.(aaaaaaaa).zamf', remove_content=False)
    'foo.bar.what.[AAAAAAAA].zamf'

    >>> remove_braces('foo.bar.what.(88888888).zamf', preserve_checksum=False)
    'foo.bar.what.zamf'

    >>> remove_braces('The Band - Let Me Out - 1993 (Vinyl - MP3 - V0 (VBR)) (1).torrent', remove_content=False)
    'The.Band.-.Let.Me.Out.-.1993.Vinyl.-.MP3.-.V0.VBR.1.torrent'

    >>> remove_braces('The Band - Let Me Out - 1993 (Vinyl - MP3 - V0 (VBR)) (1).torrent', remove_content=True)
    'The.Band.-.Let.Me.Out.-.1993.torrent'

    >>> remove_braces('Able Baker [1981].mkv', remove_content=False)
    'Able.Baker.1981.mkv'

    >>> remove_braces('Able Baker [1981].mkv', remove_content=True)
    'Able.Baker.mkv'

    """
    brace_stack = Stack()
    content_stack = Stack()
    output = ''
    for i, c in enumerate(filename):
        #print c, output, content_stack.content
        # looking for an openbracket
        if c in braces:
            brace_stack.push(braces[c])
            content_stack.push('')
        elif brace_stack:
            # looking for a closebracket
            if c == brace_stack.peek():
                brace_stack.pop()
                # contains brace content
                if is_checksum(content_stack.peek()):
                    if preserve_checksum:
                        # append the checksum to the output
                        content_stack.push('[' + content_stack.pop().upper() + ']')
                    else:
                        content_stack.pop()
                else:
                    # other content inside brackets
                    if remove_content:
                        content_stack.pop()
                        # remove the content
                    else:
                        content_stack.push('')
            else:
                content_stack.replace_first(content_stack.peek() + c)
        else:
            # new character, and we're free of brackets
            if content_stack:
                while content_stack:
                    output = dotjoin(output, content_stack.lastitem())
                output = output + '.'
            output += c

    output = endot(output)
    return output

def dotjoin(*args):
    stripped = [ a.strip('. ') for a in args if a]
    return '.'.join(stripped)

def endot(string):
    string = string.replace(' ', '.')
    while '..' in string:
        string = string.replace('..', '.')
    return string

class Stack:
    content = []

    def __nonzero__(self):
        return bool(self.content)

    def push(self, item):
        self.content = [item] + self.content

    def pop(self):
        item = self.content[0]
        self.content = self.content[1:]
        return item

    def peek(self):
        if self.content:
            return self.content[0]
        else:
            return ''

    def append(self, item):
        self.content.append(item)

    def replace_first(self, item):
        if self.content:
            self.content[0] = item
        else:
            self.content = [item]

    def lastitem(self):
        item = self.content[-1]
        self.content = self.content[:-1]
        return item

if __name__ == '__main__':
    import doctest
    doctest.testmod()

