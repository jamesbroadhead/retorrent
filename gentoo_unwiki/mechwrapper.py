#!/usr/bin/python
""" Wrapper around mechanize to make it a little more user-friendly"""

import cookielib	
import time
import warnings

import mechanize

default_useragent = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) ' + \
			'Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'

def getpage(browser, link, codes=None):
	""" wraps mechanize.browser.open(), repeats call on failure with 
	incremental hold-off.
	"""
	if codes is None: 
		codes = []	
	
	try:
		response = browser.open(link)
	except mechanize.HTTPError, error:
		if len(codes) < 4:
			time.sleep( 5 * (len(codes)+1))
			return getpage(browser, link, codes+[error.code])
		
		print 'Tried '+(len(codes)+1)+' times, with HTTP codes: ' + \
				','.join(codes)	
		raise

	return response
	
def setup_browser(useragent=default_useragent):
	""" Prepares and returns a mechanize.browser object with the given useragent
	"""
	# Browser & Cookie Jar
	browser = mechanize.Browser()
	cookiejar = cookielib.LWPCookieJar()
	browser.set_cookiejar(cookiejar)

	# Browser options
	browser.set_handle_equiv(True)
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		browser.set_handle_gzip(True)
	browser.set_handle_redirect(True)
	browser.set_handle_referer(True)
	browser.set_handle_robots(False)
	browser.set_handle_refresh(True, max_time=None, honor_time=False)

	# Debugging messages
	#browser.set_debug_http(True)
	#browser.set_debug_redirects(True)
	#browser.set_debug_responses(True)

	# User-Agent 
	browser.addheaders = [('User-agent', useragent)]
	return browser
	
if __name__ == '__main__':
	print 'This is not intended to be run directly.'
