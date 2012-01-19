"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime 

from django.test import TestCase
from polls.models import Poll

class TestPollsModel(TestCase):
	''' def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
	'''
	def test_create_poll_and_save_to_db(self):
		poll_q = 'What\'s up?'
		poll_pub_date = datetime.datetime.now()	
		
		poll = Poll()
		poll.question = poll_q 
		poll.pub_date = poll_pub_date
		poll.save()

		all_polls_in_db = Poll.objects.all()
		self.assertEquals(len(all_polls_in_db),1)

		db_poll = all_polls_in_db[0]
		self.assertEquals(db_poll,poll)
		#self.assertEquals(db_poll.question.max_length, Poll.question_max_length)
		self.assertEquals(db_poll.question,poll_q)
		self.assertEquals(db_poll.pub_date,poll_pub_date)
		
		# Test question max_length
		# TODO
	
	def test_verbose_name_for_pub_date(self):
		for field in Poll._meta.fields:
			if field.name == 'pub_date':
				self.assertEquals(field.verbose_name, 'Date published')

	def test_poll_objects_are_named_after_their_question(self):
		p = Poll()
		p.question = 'How is babby formed?'
		self.assertEquals(unicode(p), 'How is babby formed?')
