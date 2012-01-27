#!/usr/bin/python

import mechanize

from pprint import pprint 

from gwiki import GentooWiki
from mechwrapper import setup_browser, getpage

class gw_info(GentooWiki):
	info_indexpage = 'http://www.gentoo-wiki.info/Index:Index'

	info_catpage =  'http://www.gentoo-wiki.info/Category:Browse_categories'	

	browser = setup_browser()
	
	@classmethod
	def test_connection(self):
		# Test fetching from g-w.info
		try:
			info_response = getpage(self.browser, self.info_catpage)
			info_response_out = info_response.read()
		
		except mechanize.RobotExclusionError:
			print 'gentoo-wiki.info denied access with robots.txt'
			info_response_out = ''
		
		# TODO: Use BS to parse
		pprint(info_response_out)		
