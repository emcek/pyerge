from argparse import Namespace
from logging import debug, info
from re import search
from time import strftime
from typing import List, Tuple

from pyerge import utils, TMPLOGFILE, TMERGE_LOGFILE, DEVNULL


def emerge(arguments: List[str], build=True) -> Tuple[bytes, bytes]:
    """
    Run emerge command.

    :param arguments:
    :param build:
    :return:
    """
    info(f"running emerge with: {' '.join(arguments)}")
    cmd = f"sudo /usr/bin/emerge --nospinner {' '.join(arguments)}"
    if build:
        return_code, stderr = utils.run_cmd(cmd, use_system=True)
        debug(f'RC: {return_code.decode("utf-8")}, Errors: {stderr.decode("utf-8")}')
        return return_code, stderr
    output, stderr = utils.run_cmd(cmd)
    return output, stderr


# <=><=><=><=><=><=><=><=><=><=><=><=> chk_upd <=><=><=><=><=><=><=><=><=><=><=><=>
def check_upd(local_chk: bool) -> None:
    """
    Check system updates.

    :param local_chk:
    """
    utils.delete_content(TMPLOGFILE)
    utils.delete_content(TMERGE_LOGFILE)
    with open(file=TMPLOGFILE, mode='w', encoding='utf-8') as tmp, open(file=TMERGE_LOGFILE, mode='w', encoding='utf-8') as log:
        tmp.write(strftime('%a %b %d %H:%M:%S %Z %Y') + '\n')
        if not local_chk:
            info('Start syncing portage...')
            debug(f'sudo eix-sync >> {TMPLOGFILE} > {DEVNULL}')
            utils.run_cmd(f'sudo eix-sync >> {TMPLOGFILE} > {DEVNULL}', use_system=True)
        info('Checking updates...')
        output, error = emerge('-pvNDu --color n --with-bdeps=y @world'.split(), build=False)
        debug(f'Error: {error}')  # type: ignore
        log.write(output.decode('utf-8'))
        log.write(error.decode('utf-8'))

    info('Creating log file...')
    debug(f'cat {TMERGE_LOGFILE} >> {TMPLOGFILE}')
    utils.run_cmd(f'cat {TMERGE_LOGFILE} >> {TMPLOGFILE}', use_system=True)
    debug(f'cat {TMERGE_LOGFILE} | genlop -pn >> {TMPLOGFILE}')
    utils.run_cmd(f'cat {TMERGE_LOGFILE} | genlop -pn >> {TMPLOGFILE}', use_system=True)


# <=><=><=><=><=><=><=><=><=><=><=><=> tmerge <=><=><=><=><=><=><=><=><=><=><=><=>
def post_emerge(args: List[str], return_code: bytes) -> None:
    """
    Run actions after emerge.

    :param args:
    :param return_code:
    """
    pretend, world = check_emerge_opts(args)
    if not int(return_code) and not pretend and world:
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
        output, error = emerge(['-pc'], build=False)
        info('Deep clean')
        info(f'Output details:{output.decode("utf-8")}')
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
                emerge(['-c'] + package_list, build=True)
            else:
                info('Nothing to clean')
                debug(f'All packages: {regexp.group(1)}')


def check_emerge_opts(args: List[str]) -> Tuple[bool, bool]:
    """
    Check options in emerge command.

    :param args:
    :return:
    """
    return bool('pretend' in ' '.join(args)), bool('world' in ' '.join(args))


def is_portage_running() -> bool:
    """
    Check if potrage command in currently running.

    :return: True if it is running, False otherwise
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
        ret_code, _ = emerge(emerge_opts, build=True)
        post_emerge(emerge_opts, ret_code)
        if opts.deep_print or opts.deep_run:
            deep_clean(emerge_opts, opts, ret_code)


def run_check(opts: Namespace) -> None:
    """
    Run checking system updates.

    :param opts: cli arguments
    """
    if opts.action == 'check' and (opts.online or opts.local):
        check_upd(opts.local)
