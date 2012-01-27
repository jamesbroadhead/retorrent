#!/usr/bin/python

""" Interface to either wiki """


from abc import abstractmethod, ABCMeta

class GentooWiki:
	
	__metaclass__ = ABCMeta

	@abstractmethod
	def test_connection(self):
		pass

