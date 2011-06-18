

class debugprinter:
	
	def __init__(self, debug):
		self.debug = debug
		self.debugprint('Initing a debugprinter')	

	def debugprint(self, str, listol=[]):
			if self.debug:
				print str
				
				for list in listol:
					print list

	def dprint(self,str,listol=[]):
		self.debugprint(str,listol)
