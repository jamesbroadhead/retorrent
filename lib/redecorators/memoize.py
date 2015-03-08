""" redecorators.memoize """

import functools

def memoize(obj):
    cache = obj.cache = {}

    # preserve docstring and name for doctest
    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        # looks like this doesn't sort kwargs ...
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer

def memoize_record_interactive(obj):
    """ memoize, but only if a kwarg:interactive=True is passed """

    cache = obj.cache = {}

    # preserve docstring and name for doctest
    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        # looks like this doesn't sort kwargs ...

        key = str(args)
        if key in cache:
            return cache[key]

        res = obj(*args, **kwargs)
        if 'interactive' in kwargs and kwargs['interactive']:
            cache[key] = res
        return res

    return memoizer
