#!/usr/bin/env python
"""
Usage:
    is_seeded TARGETS...
    is_seeded -u TARGETS...

Options:
    -u, --only-unseeded


"""
import sys

from docopt import docopt

from .. import seededlib


def _main(only_unseeded, targets):

    seeded, unseeded = seededlib.is_seeded(targets)

    if only_unseeded:
        print(' '.join(['"%s"' % (u,) for u in unseeded]))
    else:
        print("Seeded:")
        for k, v in sorted(seeded.items()):
            print("\t %s => %s" % (k, v))
        print("Unseeded:")
        for j in unseeded:
            print("\t", j)

    # nothing is unseeded - is_seeded returns true
    if not unseeded:
        return 0
    return 1


def main():
    arguments = docopt(__doc__)
    sys.exit(_main(arguments['--only-unseeded'], arguments['TARGETS']))


if __name__ == '__main__':
    main()
