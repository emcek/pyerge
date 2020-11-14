#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
import sys
from argparse import ArgumentParser, Namespace
from logging import basicConfig, DEBUG, info, error
from typing import List

from pyerge import tmerge, utils, __version__
from pyerge.glsa import run_glsa

basicConfig(format='%(asctime)s | %(levelname)-6s | %(message)s', level=DEBUG)


def run_parser() -> None:
    """
    Function to collect command line arguments.

    Construct main object with correct set of parameters.
    """
    parser = ArgumentParser(description='Emerge in temporary RAM disk')
    parser.add_argument('-s', '--size', action='store', dest='size',
                        default='4G', help='Size or RAM disk, default 4G')
    parser.add_argument('-l', '--check_local', action='store_true', dest='local',
                        default=False, help='check locally')
    parser.add_argument('-d', '--deep_clean', action='store_true', dest='deep',
                        default=False, help='run deep clean after emerge')
    parser.add_argument('-w', '--world', action='store_true', dest='world',
                        default=False, help='run emerge -NDu @world')
    parser.add_argument('-r', '--pretend_world', action='store_true', dest='pretend_world',
                        default=False, help='run emerge -pvNDu @world')
    parser.add_argument('-p', '--pretend', action='store_true', dest='pretend',
                        default=False, help='add --pretend/-p to emerge')
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet',
                        default=False, help='add --quiet/-q to emerge')
    parser.add_argument('-v', '--verbose', action='count', dest='verbose',
                        default=0, help='Increase output verbosity')
    parser.add_argument('-e', '--elements', action='store', dest='elements', type=int,
                        default='5', help='number of elements')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('action', help='check, emerge, glsa_list or glsa_test')
    opts, emerge_opts = parser.parse_known_args()
    if opts.action not in ['check', 'emerge', 'glsa_list', 'glsa_test']:
        error(f'Wrong options: {opts} {emerge_opts}')
        sys.exit(1)
    main_exec(opts, emerge_opts)


def main_exec(opts: Namespace, emerge_opts: List[str]) -> None:
    """
    Main execution function.

    :param opts: cli arguments
    :param emerge_opts: list of arguments for emege
    """
    if opts.world:
        emerge_opts = ['-NDu', '@world']
    if opts.pretend_world:
        emerge_opts = ['-pvNDu', '@world']
    if opts.pretend:
        emerge_opts[0] += 'p' if emerge_opts[0][0] == '-' else '-p'
    if opts.quiet:
        emerge_opts[0] += 'q' if emerge_opts[0][0] == '-' else '-q'
    if opts.verbose:
        info(f'Pyerge version: {__version__}')
    opts.online = utils.is_internet_connected(opts.verbose)
    if opts.action in ('glsa_list', 'glsa_test'):
        print(run_glsa(opts))
        sys.exit(0)

    if not tmerge.is_portage_running():
        utils.set_portage_tmpdir()
        utils.handling_mounting(opts)
        tmerge.run_emerge(emerge_opts, opts)
        tmerge.run_check(opts)
        utils.unmounttmpfs(opts)
    else:
        if opts.verbose:
            info('emerge already running!')
