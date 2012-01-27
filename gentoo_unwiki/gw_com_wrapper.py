#!/usr/bin/python

from pprint import pprint

from gwiki import GentooWiki

from wikitools import api, wiki, APIError, APIDisabled
from wikiwrapper import wikiparams_siteinfo 

class gw_com(GentooWiki):
	com_catpage =   'http://en.gentoo-wiki.com/wiki/Category:Browse_Categories'	
	com_indexpage = 'http://en.gentoo-wiki.com/wiki/Category:Index'
	com_api =       'http://en.gentoo-wiki.com/w/api.php'	

	@classmethod
	def test_connection(self):
		# Test fetching from g-w.com
		com_wikisite = wiki.Wiki(self.com_api)
		
		try:
			wikireq = api.APIRequest(com_wikisite, wikiparams_siteinfo)
			com_response_out = wikireq.query(querycontinue=False)
		
		except APIDisabled:
			print 'gentoo-wiki.com has disabled their API'
			return False
		
		except APIError:
			
			# TODO Wrap wikisite.APIRequest & handle APIError better. Need test site
			# APIError: 
			#  If a multipart request is made and the poster module is not available
			#  When trying to change the result format using changeParam
			#  When the MediaWiki API returns an error
			
			print 'gentoo-wiki.com\'s API returned an error'
			return False	

		print 'gentoo-wiki.com output:'	
		pprint(com_response_out)
		return True
