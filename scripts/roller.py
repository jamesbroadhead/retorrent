#!/usr/bin/python
import numpy

def roll(ndice):
	a=[numpy.random.randint(0,10) for i in range(ndice) ]
	a.sort()
	return a

def nsuccess(rolls,succ):
	successes = 0

	for roll in rolls:
		if roll >= succ : 
			successes += 1
		elif roll == 1:
			successes -= 1
	
	return successes


distr = [0,0,0,0,0,0,0,0,0,0,0,0]

for i in range(100000):			
		thistime=0
		while nsuccess(roll(5),6) > 0:
			thistime += 1
		if thistime > 10:
			thistime = 10
		distr[thistime] = distr[thistime] + 1	

		print distr	
