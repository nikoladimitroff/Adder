class InvalidArgumentError(Exception):
    pass

def memoize(func):
    arg_table = {}
    def memoized(*args):
        if args not in arg_table:
            arg_table[args] = func(*args)

        return arg_table[args]

    return memoized