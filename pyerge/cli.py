#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from argparse import ArgumentParser, Namespace
from logging import basicConfig, DEBUG, info, error
from typing import List

from pyerge import tmerge, utils, glsa, __version__

basicConfig(format='%(asctime)s | %(levelname)-6s | %(message)s', level=DEBUG)


def run_parser():
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
    parser.add_argument('-v', '--verbose', action='count', dest='verbose',
                        help='Increase output verbosity')
    parser.add_argument('-e', '--elements', action='store', dest='elements', type=int,
                        default='5', help='number of elements')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('action', help='check, emerge, glsa_list or glsa_test')
    opts, emerge_opts = parser.parse_known_args()
    if opts.action not in ['check', 'emerge', 'glsa_list', 'glsa_test']:
        error(f'Wrong options: {opts} {emerge_opts}')
        exit()

    if opts.world:
        emerge_opts = ['-NDu', '@world']
    if opts.pretend_world:
        emerge_opts = ['-pvNDu', '@world']

    info(f'Pyerge version: {__version__}')
    opts.online = utils.is_internet_connected(opts.verbose)
    if opts.action in ('glsa_list', 'glsa_test'):
        run_glsa(opts)
        exit()

    if not tmerge.is_portage_running():
        utils.set_portage_tmpdir()
        handling_mounting(opts)
        run_emerge(emerge_opts, opts)
        run_check(opts)
        utils.unmounttmpfs(opts.size, opts.verbose)
    else:
        if opts.verbose:
            info('emerge already running!')


def handling_mounting(opts: Namespace) -> None:
    """
    Handling mounting temporary file fistem with requestes size.

    :param opts: cli arguments
    """
    if not opts.local:
        if not utils.is_tmpfs_mounted():
            utils.mounttmpfs(opts.size, opts.verbose)
        elif utils.size_of_mounted_tmpfs() != utils.convert2blocks(opts.size):
            utils.remounttmpfs(opts.size, opts.verbose)
        else:
            if opts.verbose:
                info('tmpfs is already mounted with requested size!')


def run_emerge(emerge_opts: List[str], opts: Namespace) -> None:
    """
    Run update of system.

    :param emerge_opts: list of arguments for emege
    :param opts: cli arguments
    """
    if opts.action == 'emerge' and opts.online:
        ret_code = tmerge.emerge(emerge_opts, opts.verbose, build=True)
        tmerge.post_emerge(emerge_opts, opts.verbose, ret_code)
        if opts.deep:
            tmerge.deep_clean(emerge_opts, opts.verbose, ret_code)


def run_check(opts: Namespace) -> None:
    """
    Run checking system updates.

    :param opts: cli arguments
    """
    if opts.action == 'check' and (opts.online or opts.local):
        tmerge.check_upd(opts.local, opts.verbose)


def run_glsa(opts: Namespace) -> None:
    """
    Run gGLSA module to test or to list.

    :param opts: cli arguments
    """
    if opts.online:
        try:
            attr = getattr(glsa, opts.action)
        except AttributeError:
            pass
        else:
            print(attr(opts))
