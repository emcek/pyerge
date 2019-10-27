#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from argparse import Namespace
from logging import debug, info
from time import strftime
from typing import List, Tuple

from pyerge import utils, tmplogfile, tmerge_logfile, dev_null


def emerge(arguments: List[str], verbose: int, build=True) -> Tuple[bytes, bytes]:
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
        return_code, stderr = utils.run_cmd(cmd, use_system=True)
        if verbose > 1:
            debug(f'RC: {return_code.decode("utf-8")}, Errors: {stderr.decode("utf-8")}')
        return return_code, stderr
    output, stderr = utils.run_cmd(cmd)
    return output, stderr


# <=><=><=><=><=><=><=><=><=><=><=><=> chk_upd <=><=><=><=><=><=><=><=><=><=><=><=>
def check_upd(local_chk: bool, verbose: int) -> None:
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
        if verbose > 1:
            debug(f'sudo eix-sync >> {tmplogfile} > {dev_null}')
        utils.run_cmd(f'sudo eix-sync >> {tmplogfile} > {dev_null}', use_system=True)
    if verbose:
        info('Checking updates...')
    output, error = emerge('-pvNDu --color n @world'.split(), verbose, build=False)
    if verbose > 1:
        debug(f'Error: {error}')
    log.write(output.decode('utf-8'))
    log.write(error.decode('utf-8'))
    tmp.close()
    log.close()

    if verbose:
        info('Creating log file...')
    if verbose > 1:
        debug(f'cat {tmerge_logfile} >> {tmplogfile}')
    utils.run_cmd(f'cat {tmerge_logfile} >> {tmplogfile}', use_system=True)
    if verbose > 1:
        debug(f'cat {tmerge_logfile} | genlop -pn >> {tmplogfile}')
    utils.run_cmd(f'cat {tmerge_logfile} | genlop -pn >> {tmplogfile}', use_system=True)


# <=><=><=><=><=><=><=><=><=><=><=><=> tmerge <=><=><=><=><=><=><=><=><=><=><=><=>
def post_emerge(args: List[str], verbose: int, return_code: bytes) -> None:
    """
    Run actions after emerge.

    :param args:
    :param verbose:
    :param return_code:
    """
    pretend, world = check_emerge_opts(args)
    if not int(return_code) and not pretend and world:
        if verbose:
            info('Clearing emerge log')
        tmp = open(tmplogfile, 'w')
        log = open(tmerge_logfile, 'w')
        log.write('Total: 0 packages, Size of downloads: 0 KiB')
        tmp.close()
        log.close()


def deep_clean(args: List[str], verbose: int, return_code: bytes) -> None:
    """
    Run deep clean after emerge.

    :param args:
    :param verbose:
    :param return_code:
    """
    pretend, world = check_emerge_opts(args)
    if not int(return_code) and not pretend and world:
        output, error = emerge(['-pc'], verbose, build=False)
        if verbose:
            info('Deep clean')
        if verbose > 1:
            debug(f'Output details:{output.decode("utf-8")}')
            debug(f'Errors details:{error.decode("utf-8")}')


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


def run_emerge(emerge_opts: List[str], opts: Namespace) -> None:
    """
    Run update of system.

    :param emerge_opts: list of arguments for emege
    :param opts: cli arguments
    """
    if opts.action == 'emerge' and opts.online:
        ret_code, _ = emerge(emerge_opts, opts.verbose, build=True)
        post_emerge(emerge_opts, opts.verbose, ret_code)
        if opts.deep:
            deep_clean(emerge_opts, opts.verbose, ret_code)


def run_check(opts: Namespace) -> None:
    """
    Run checking system updates.

    :param opts: cli arguments
    """
    if opts.action == 'check' and (opts.online or opts.local):
        check_upd(opts.local, opts.verbose)
