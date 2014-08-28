class AdderError(Exception):
    pass

class InvalidArgumentError(AdderError):
    pass

class ParsingError(AdderError):
    pass

def memoize(func):
    cache = {}
    def memoized(arg):
        if cache.get(arg) is None:
            cache[arg] = func(arg)
        return cache[arg]
    return memoized
