"""
Originally from:
http://stackoverflow.com/questions/862807/how-would-you-write-a-debuggable-decorator-in-python

"""
import functools
import logging


def tracelogdecorator(f):
    tracelogger = logging.getLogger("tracelog")

    # preserve docstring and name for doctest
    @functools.wraps(f)
    def _tracelogdecorator(*arg, **kwargs):
        tracelogger.log(logging.INFO, "calling '%s'(%r,%r)", f.__name__, arg, kwargs)
        ret = f(*arg, **kwargs)
        tracelogger.log(logging.INFO, "called '%s'(%r,%r) got return value: %r", f.__name__, arg,
                        kwargs, ret)
        return ret

    return _tracelogdecorator
