#!/usr/bin/python

""" gentoo-unwiki.py is a web-crawling script attempting to detect duplicate
articles in the gentoo-wiki dump, to aid in their removal, and the preservation
of other content. 

== Rationale ==
Some time ago, gentoo-wiki.com suffered a catastrophic failure. 
gentoo-wiki.info was set up to pull as much content as possible from the 
google cache and elsewhere, but the wikisource was lost. 

Since then, many pages have been recreated but not all that were at g-w.com 
before the crash. Now, an official wiki exists at wiki.gentoo.org, and we are
transitioning there. It is time for gentoo-wiki.info to be shut down, as its
usefulness has passed. Indeed, much of its content is out of date, and it ranks
high in searches.

This script is intended to traverse g-w.info and compare the content against 
gentoo-wiki.com. As neither are hosted by the gentoo foundation, it should be 
used with care.

Note: 
	Will probably use wikitools for g-w.com / w.g.org 
	Must use mechanize for g-w.info.

With content from:
	http://stockrt.github.com/p/emulating-a-browser-in-python-with-mechanize/
"""

from gw_com_wrapper import gw_com
from gw_info_wrapper import gw_info

def main():
	""" Will: Perform setup, crawling and handles output. 
	Currently: Connects to both servers and checks that it can fetch pages
	"""	
	com = gw_com()
	info = gw_info()

	com.test_connection()
	info.test_connection()
	

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
