import sys
from argparse import ArgumentParser, Namespace
from logging import basicConfig, DEBUG, INFO, ERROR, info, error
from typing import List

from pyerge import tmerge, utils, __version__


def run_parser() -> None:
    """
    Function to collect command line arguments.

    Construct main object with correct set of parameters.
    """
    parser = ArgumentParser(description='Emerge in temporary RAM disk')
    parser.add_argument('-s', '--size', action='store', dest='size', default='4G', help='Size or RAM disk, default 4G')
    parser.add_argument('-l', '--check_local', action='store_true', dest='local', default=False, help='check locally')
    parser.add_argument('-d', '--clean-print', action='store_true', dest='deep_print', default=False, help='print deep clean info after emerge')
    parser.add_argument('-c', '--clean-run', action='store_true', dest='deep_run', default=False, help='run deep clean after emerge')
    parser.add_argument('-w', '--world', action='store_true', dest='world', default=False, help='run emerge -NDu @world')
    parser.add_argument('-r', '--pretend_world', action='store_true', dest='pretend_world', default=False, help='run emerge -pvNDu @world')
    parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', default=False, help='no output from pyerge itself only form other tools')
    parser.add_argument('-v', '--verbose', action='count', dest='verbose', default=0, help='Increase output verbosity')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('action', help='check or emerge')
    opts, emerge_opts = parser.parse_known_args()
    level = DEBUG if opts.verbose else INFO
    if opts.quiet:
        level = ERROR
    basicConfig(format='%(asctime)s | %(levelname)-6s | %(message)s', level=level)
    if opts.action not in ['check', 'emerge']:
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
        emerge_opts = ['--with-bdeps=y', '--keep-going=y', '--newuse', '--deep', '--update', '@world']
    if opts.pretend_world:
        emerge_opts = ['--with-bdeps=y', '--pretend', '--verbose', '--newuse', '--deep', '--update', '@world']
    info(f'Pyerge version: {__version__}')
    opts.online = utils.is_internet_connected()

    if not tmerge.is_portage_running():
        utils.set_portage_tmpdir()
        utils.handling_mounting(opts)
        tmerge.run_emerge(emerge_opts, opts)
        tmerge.run_check(opts)
        utils.unmounttmpfs(opts)
    else:
        info('emerge already running!')
