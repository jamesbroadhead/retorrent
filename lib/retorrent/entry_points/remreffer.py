#!/usr/bin/env python
""" remreffer: recursive rm """
import sys

from ..remreffer import remref


def main():
    try:
        sys.exit(remref(sys.argv[1:]))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
