# Originally from: http://stackoverflow.com/questions/862807/how-would-you-write-a-debuggable-decorator-in-python

import logging

def tracelogdecorator(f):
	tracelogger = logging.getLogger("tracelog")
	def _tracelogdecorator(*arg,**kwargs):
		tracelogger.log(logging.INFO, "calling '%s'(%r,%r)", f.func_name, arg, kwargs)
		ret=f(*arg,**kwargs)
		tracelogger.log(logging.INFO, "called '%s'(%r,%r) got return value: %r", f.func_name, arg, kwargs, ret)
		return ret
	return _tracelogdecorator
