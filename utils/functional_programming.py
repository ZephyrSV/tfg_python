from functools import reduce

def flatten(l):
    return [item for sublist in l for item in sublist]
def lmap(f, l):
    """ Short hand for list(map(f, l))
    """
    return list(map(f,l))

def compose(*fs):
    """ Composes functions

    compose(f, g)(x) = f(g(x))
    """
    return lambda x: reduce(lambda acc, f: f(acc), fs, x)

def dropWhile(f, l):
    """ Drops elements from the list while the predicate is true
    """
    if len(l) == 0:
        return []
    elif f(l[0]):
        return dropWhile(f, l[1:])
    else:
        return l
