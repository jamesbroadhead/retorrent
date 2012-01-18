from functional_tests import FunctionalTest, ROOT
from selenium.webdriver.common.keys import Keys

class TestPollsAdmin(FunctionalTest):
	def test_can_create_new_poll_via_admin_site(self):

		self.browser.get(ROOT + '/admin/')

		body = self.browser.find_element_by_tag_name('body')
		self.assertIn('Django administration', body.text)
	
		username_field = self.browser.find_element_by_name('username')
		username_field.send_keys('admin')

		password_field = self.browser.find_element_by_name('password')
		password_field.send_keys('adm1n')
		password_field.send_keys(Keys.RETURN)
		
		# a few links called Polls
		polls_links = self.browser.find_elements_by_link_text('Polls')
		self.assertEquals(len(polls_links), 2)

		self.fail('todo: Make more tests')

class TestSitesAdmin(FunctionalTest):
	
	def test_two_sites_links(self):	
		self.browser.get(ROOT + '/admin/')

		body = self.browser.find_element_by_tag_name('body')
		self.assertIn('Django administration', body.text)
	
		username_field = self.browser.find_element_by_name('username')
		username_field.send_keys('admin')
		password_field = self.browser.find_element_by_name('password')
		password_field.send_keys('adm1n')
		password_field.send_keys(Keys.RETURN)
		
		# a few links called Polls
		sites_links = self.browser.find_elements_by_link_text('Sites')
		self.assertEquals(len(sites_links), 2)
