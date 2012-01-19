from django.db import models

# Create your models here.

class Poll(models.Model):
	question_max_length = 200
	question = models.CharField(\
			max_length=question_max_length)
	
	pub_date = models.DateTimeField(verbose_name='Date published')
	

	def __unicode__(self):
		return self.question
