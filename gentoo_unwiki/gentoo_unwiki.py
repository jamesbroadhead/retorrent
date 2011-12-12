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

import pprint 

import mechanize

from wikitools import api, wiki, APIError, APIDisabled

from mechwrapper import setup_browser, getpage
from wikiwrapper import wikiparams_siteinfo 

def main():
	""" Will: Perform setup, crawling and handles output. 
	Currently: Connects to both servers and checks that it can fetch pages
	"""	
	
	info_catpage =  'http://www.gentoo-wiki.info/Category:Browse_categories'	
	info_indexpage = 'http://www.gentoo-wiki.info/Index:Index'

	com_catpage =   'http://en.gentoo-wiki.com/wiki/Category:Browse_Categories'	
	com_indexpage = 'http://en.gentoo-wiki.com/wiki/Category:Index'
	com_api =       'http://en.gentoo-wiki.com/w/api.php'	
	
	browser = setup_browser()
	
	# Test fetching from g-w.info
	try:
		info_response = getpage(browser, info_catpage)
		info_response_out = info_response.read()
	
	except mechanize.RobotExclusionError:
		print 'gentoo-wiki.info denied access with robots.txt'
		info_response_out = ''
	
	# Test fetching from g-w.com
	com_wikisite = wiki.Wiki(com_api)
	
	try:
		wikireq = api.APIRequest(com_wikisite, wikiparams_siteinfo)
		com_response_out = wikireq.query(querycontinue=False)
	except APIDisabled:
		print 'gentoo-wiki.com has disabled their API'
		com_response_out = ''
	except APIError:
		# TODO Wrap wikisite.APIRequest & handle APIError better. Need test site
		# APIError: 
		#  If a multipart request is made and the poster module is not available
		#  When trying to change the result format using changeParam
		#  When the MediaWiki API returns an error
		
		print 'gentoo-wiki.com\'s API returned an error'
		com_response_out = ''

	print 'gentoo-wiki.info output:'	
	pprint.pprint(info_response_out)

	print 'gentoo-wiki.com output:'	
	pprint.pprint(com_response_out)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
