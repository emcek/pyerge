#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from argparse import ArgumentParser

from pyerge import __version__


def run():
    """
    Function to collect command line arguments.

    Construct main object with correct set of parameters.
    """
    parser = ArgumentParser(description='Pyerge')
    parser.add_argument('-s', '--size', action='store', dest='size',
                        default='4G', help='Size or RAM disk, default 4G')
    parser.add_argument('-l', '--check_local', action='store_true', dest='local',
                        default=False, help='check locally')
    parser.add_argument('-d', '--deep_clean', action='store_true', dest='deep',
                        default=False, help='no deep clean')
    parser.add_argument('-w', '--world', action='store_true', dest='world',
                        default=False, help='run emerge -NDu @world')
    parser.add_argument('-r', '--pretend_world', action='store_true', dest='pretend_world',
                        default=False, help='run emerge -pvNDu @world')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
                        default=False, help='Show more data')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('action', help='check or emerge')
    opts, emerge_opts = parser.parse_known_args()
    print(opts, emerge_opts)


if __name__ == '__main__':
    run()
