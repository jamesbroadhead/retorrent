import functools

def memoize(obj):
    cache = obj.cache = {}

    # preserve docstring and name for doctest
    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        # looks like this doesn't sort kwargs ...
        key = str(args) + str(kwargs)
        print key
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer

def memoize_ignore_kwargs(obj):
    cache = obj.cache = {}

    # preserve docstring and name for doctest
    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        # looks like this doesn't sort kwargs ...
        key = str(args)
        print key
        print cache
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer
