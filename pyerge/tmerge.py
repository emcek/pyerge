#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from argparse import ArgumentParser
from logging import debug, basicConfig, warning, DEBUG, info, error
from os import environ
from time import strftime
from typing import List, Tuple

from pyerge import utils, __version__, portage_tmpdir, tmplogfile, tmerge_logfile, dev_null

basicConfig(format='%(asctime)s | %(levelname)-6s | %(message)s', level=DEBUG)


def emerge(arguments: List[str], verbose: bool, build=True) -> bytes:
    """
    Run emerge command.

    :param arguments:
    :param verbose:
    :param build:
    :return:
    """
    if verbose:
        info(f"running emerge with: {' '.join(arguments)}")
    cmd = f"sudo /usr/bin/emerge --nospinner {' '.join(arguments)}"
    if build:
        return_code, _ = utils.run_cmd(cmd, use_system=True)
        return return_code
    output, _ = utils.run_cmd(cmd)
    return output


# <=><=><=><=><=><=><=><=><=><=><=><=> chk_upd <=><=><=><=><=><=><=><=><=><=><=><=>
def check_upd(local_chk: bool, verbose: bool) -> None:
    """
    Check system updates.

    :param local_chk:
    :param verbose:
    """
    utils.delete_content(tmplogfile)
    utils.delete_content(tmerge_logfile)
    tmp = open(tmplogfile, 'w')
    log = open(tmerge_logfile, 'w')
    tmp.write(strftime('%a %b %d %H:%M:%S %Z %Y') + '\n')
    if not local_chk:
        if verbose:
            # info('Start syncing overlays...')
            # utils.run_cmd(f'sudo layman -SN >> {tmplogfile} > {dev_null}', use_subproc=False)
            info('Start syncing portage...')
            debug(f'sudo eix-sync >> {tmplogfile} > {dev_null}')
        utils.run_cmd(f'sudo eix-sync >> {tmplogfile} > {dev_null}', use_system=True)
        if verbose:
            info('Checking updates...')
    output = emerge('-pvNDu --color n @world'.split(), verbose, build=False)
    if verbose:
        info('Updates checked')
    log.write(output.decode(encoding='utf-8'))
    tmp.close()
    log.close()

    if verbose:
        info('Creating log file...')
        debug(f'cat {tmerge_logfile} >> {tmplogfile}')
    utils.run_cmd(f'cat {tmerge_logfile} >> {tmplogfile}', use_system=True)
    if verbose:
        debug(f'cat {tmerge_logfile} | genlop -pn >> {tmplogfile}')
    utils.run_cmd(f'cat {tmerge_logfile} | genlop -pn >> {tmplogfile}', use_system=True)
    if verbose:
        info('Wrote to logs file')


# <=><=><=><=><=><=><=><=><=><=><=><=> tmerge <=><=><=><=><=><=><=><=><=><=><=><=>
def post_emerge(args: List[str], verbose: bool, return_code: bytes) -> None:
    """
    Run actions after emerge.

    :param args:
    :param verbose:
    :param return_code:
    """
    pretend, world = check_emerge_opts(args)
    if len(return_code) is 0 and not pretend and world:
        if verbose:
            info('Clearing emerge log')
        tmp = open(tmplogfile, 'w')
        log = open(tmerge_logfile, 'w')
        log.write('Total: 0 packages, Size of downloads: 0 KiB')
        tmp.close()
        log.close()


def deep_clean(args: List[str], verbose: bool, return_code: bytes) -> None:
    """
    Run deep clean after emerge.

    :param args:
    :param verbose:
    :param return_code:
    """
    pretend, world = check_emerge_opts(args)
    if len(return_code) is 0 and not pretend and world:
        out = emerge(['-pc'], verbose, build=False)
        if verbose:
            info('Deep clean')
            debug(f'Details:{out.decode(encoding="utf-8")}')


def check_emerge_opts(args: List[str]) -> Tuple[bool, bool]:
    """
    Check options in emerge command.

    :param args:
    :return:
    """
    pretend = True
    world = False
    if 'p' not in args[0] or 'f' in args[0]:
        pretend = False
    if 'world' in ' '.join(args):
        world = True
    return pretend, world


def is_portage_running() -> bool:
    """
    Check if potrage command in currently running.

    :return: True if is running, False otherwise
    """
    out, _ = utils.run_cmd('pgrep -f /usr/bin/emerge')
    return bool(out)


def set_portage_tmpdir() -> None:
    """Set system variable."""
    if environ.get('PORTAGE_TMPDIR') is None:
        environ['PORTAGE_TMPDIR'] = portage_tmpdir


if __name__ == '__main__':
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

    set_portage_tmpdir()

    if not is_portage_running():
        if not utils.is_tmpfs_mounted(portage_tmpdir):
            utils.mounttmpfs(opts.size, opts.verbose, portage_tmpdir)
        elif utils.size_of_mounted_tmpfs(portage_tmpdir) != utils.convert2blocks(opts.size):
            utils.remounttmpfs(opts.size, opts.verbose, portage_tmpdir)
        else:
            if opts.verbose:
                info('tmpfs is already mounted with requested size!')

        if opts.action == 'emerge':
            ret_code = emerge(emerge_opts, opts.verbose, build=True)
            post_emerge(emerge_opts, opts.verbose, ret_code)
            if opts.deep:
                deep_clean(emerge_opts, opts.verbose, ret_code)
        elif opts.action == 'check':
            if utils.is_internet_connected() or opts.local:
                if opts.verbose:
                    info('There is internet connecton')
                check_upd(opts.local, opts.verbose)
            else:
                if opts.verbose:
                    warning('No internet connection!\n')
    else:
        if opts.verbose:
            info('emerge already running!')
    utils.unmounttmpfs(opts.size, opts.verbose, portage_tmpdir)
