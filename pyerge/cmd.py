#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from argparse import ArgumentParser
from logging import basicConfig, warning, DEBUG, info, error

from pyerge import tmerge, utils, __version__, portage_tmpdir

basicConfig(format='%(asctime)s | %(levelname)-6s | %(message)s', level=DEBUG)


def run():
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
    if opts.world:
        emerge_opts = ['-NDu', '@world']
    if opts.pretend_world:
        emerge_opts = ['-pvNDu', '@world']

    if opts.action != 'check' and opts.action != 'emerge':
        error(f'Wrong options: {opts} {emerge_opts}')
        exit()

    tmerge.set_portage_tmpdir()

    if not tmerge.is_portage_running():
        if not utils.is_tmpfs_mounted(portage_tmpdir):
            utils.mounttmpfs(opts.size, opts.verbose, portage_tmpdir)
        elif utils.size_of_mounted_tmpfs(portage_tmpdir) != utils.convert2blocks(opts.size):
            utils.remounttmpfs(opts.size, opts.verbose, portage_tmpdir)
        else:
            if opts.verbose:
                info('tmpfs is already mounted with requested size!')

        if opts.action == 'emerge':
            ret_code = tmerge.emerge(emerge_opts, opts.verbose, build=True)
            tmerge.post_emerge(emerge_opts, opts.verbose, ret_code)
            if opts.deep:
                tmerge.deep_clean(emerge_opts, opts.verbose, ret_code)
        elif opts.action == 'check':
            if utils.is_internet_connected() or opts.local:
                if opts.verbose:
                    info('There is internet connecton')
                tmerge.check_upd(opts.local, opts.verbose)
            else:
                if opts.verbose:
                    warning('No internet connection!\n')
    else:
        if opts.verbose:
            info('emerge already running!')
    utils.unmounttmpfs(opts.size, opts.verbose, portage_tmpdir)
