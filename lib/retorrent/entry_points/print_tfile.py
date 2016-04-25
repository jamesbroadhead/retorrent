#!/usr/bin/env python
"""
Usage:
    print_tfile TARGETS...
"""
from pprint import pprint

from docopt import docopt

from ..find_tfile import tfile_details


def _main(targets):
    results = [tfile_details(target) for target in targets]
    return [r for r in results if r is not None]


def main():
    arguments = docopt(__doc__)

    pprint(_main(arguments['TARGETS']))


if __name__ == '__main__':
    main()
