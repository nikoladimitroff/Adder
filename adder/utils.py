class InvalidArgumentError(Exception):
    pass

def memoize(func):
    arg_table = {}
    def memoized(*args):
        arguments = tuple(str(arg) for arg in args)
        if arguments not in arg_table:
            arg_table[arguments] = func(*args)

        return arg_table[arguments]

    return memoized