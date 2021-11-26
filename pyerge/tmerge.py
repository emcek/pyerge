from argparse import Namespace
from logging import debug, info
from re import search
from time import strftime
from typing import List, Tuple

from pyerge import utils, TMPLOGFILE, TMERGE_LOGFILE, DEVNULL


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
    utils.delete_content(TMPLOGFILE)
    utils.delete_content(TMERGE_LOGFILE)
    with open(file=TMPLOGFILE, mode='w', encoding='utf-8') as tmp, open(file=TMERGE_LOGFILE, mode='w', encoding='utf-8') as log:
        tmp.write(strftime('%a %b %d %H:%M:%S %Z %Y') + '\n')
        if not local_chk:
            if verbose:
                info('Start syncing portage...')
            if verbose > 1:
                debug(f'sudo eix-sync >> {TMPLOGFILE} > {DEVNULL}')
            utils.run_cmd(f'sudo eix-sync >> {TMPLOGFILE} > {DEVNULL}', use_system=True)
        if verbose:
            info('Checking updates...')
        output, error = emerge('-pvNDu --color n @world'.split(), verbose, build=False)
        if verbose > 1:
            debug(f'Error: {error}')  # type: ignore
        log.write(output.decode('utf-8'))
        log.write(error.decode('utf-8'))

    if verbose:
        info('Creating log file...')
    if verbose > 1:
        debug(f'cat {TMERGE_LOGFILE} >> {TMPLOGFILE}')
    utils.run_cmd(f'cat {TMERGE_LOGFILE} >> {TMPLOGFILE}', use_system=True)
    if verbose > 1:
        debug(f'cat {TMERGE_LOGFILE} | genlop -pn >> {TMPLOGFILE}')
    utils.run_cmd(f'cat {TMERGE_LOGFILE} | genlop -pn >> {TMPLOGFILE}', use_system=True)


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
        with open(file=TMPLOGFILE, mode='w', encoding='utf-8'), open(file=TMERGE_LOGFILE, mode='w', encoding='utf-8') as log:
            log.write('Total: 0 packages, Size of downloads: 0 KiB')


def deep_clean(args: List[str], opts: Namespace, return_code: bytes) -> None:
    """
    Run deep clean after emerge.

    :param args:
    :param opts:
    :param return_code:
    """
    pretend, world = check_emerge_opts(args)
    if not int(return_code) and not pretend and world:
        output, error = emerge(['-pc'], opts.verbose, build=False)
        if opts.verbose:
            info('Deep clean')
            info(f'Output details:{output.decode("utf-8")}')
        if opts.verbose > 1:
            debug(f'Errors details:{error.decode("utf-8")}')
        deep_run(opts, output)


def deep_run(opts: Namespace, output: bytes):
    """
    Run deep clean emegre without gent0o sources.

    :param opts:
    :param output:
    """
    if opts.deep_run:
        regexp = search(r'All selected packages:\s(.*)\n', output.decode('utf-8'))
        if regexp is not None:
            package_list = [package for package in regexp.group(1).split(' ') if 'gentoo-sources' not in package]
            if package_list:
                debug(f'Cleaning {len(package_list)} packages')
                emerge(['-c'] + package_list, opts.verbose, build=True)
            else:
                info('Nothing to clean')
                debug(f'All packages: {regexp.group(1)}')


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
        if opts.deep_print or opts.deep_run:
            deep_clean(emerge_opts, opts, ret_code)


def run_check(opts: Namespace) -> None:
    """
    Run checking system updates.

    :param opts: cli arguments
    """
    if opts.action == 'check' and (opts.online or opts.local):
        check_upd(opts.local, opts.verbose)
