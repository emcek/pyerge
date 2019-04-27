#!/usr/bin/python3.6
from argparse import ArgumentParser
from logging import debug, basicConfig, warning, DEBUG, info, error
from os import environ, system
from re import search
from shlex import split
from subprocess import Popen, PIPE
from time import strftime
from typing import List, Union, Tuple

__author__ = 'emc'
__license__ = 'GPL'
__version__ = '0.3.0'

PORTAGE_TMPDIR = '/var/tmp/portage'
tmplogfile = '/var/log/portage/tmerge/tmp.emerge.log'
logfile = '/var/log/portage/tmerge/emerge.log'
SERVER1 = '89.16.167.134'
SERVER2 = '85.17.140.211'
DEVNULL = '/dev/null 2>&1'
basicConfig(format='%(asctime)s | %(levelname)-6s | %(message)s', level=DEBUG)


# <=><=><=><=><=><=><=><=><=><=><=><=> General <=><=><=><=><=><=><=><=><=><=><=><=>
def mounttmpfs(size: str, verbose: bool, port_tmp_dir: str) -> None:
    info(f'Mounting {size} of memory to {port_tmp_dir}') if verbose else None
    debug(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {port_tmp_dir}') if verbose else None
    run_cmd(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {port_tmp_dir}')


def emerge(arguments: List[str], verbose: bool, build=True) -> bytes:
    info(f"running emerge with: {' '.join(arguments)}") if verbose else None
    if build:
        return_code = system(f"sudo /usr/bin/emerge --nospinner {' '.join(arguments)}")
        return bytes(return_code)
    else:
        output = run_cmd(f"sudo /usr/bin/emerge --nospinner {' '.join(arguments)}")
        return output


def unmounttmpfs(size: str, verbose: bool, port_tmp_dir: str) -> None:
    info(f'Unmounting {size} of memory from {port_tmp_dir}') if verbose else None
    debug(f'sudo umount -f {port_tmp_dir}') if verbose else None
    run_cmd(f'sudo umount -f {port_tmp_dir}')


# <=><=><=><=><=><=><=><=><=><=><=><=> chk_upd <=><=><=><=><=><=><=><=><=><=><=><=>
def ping_test() -> bool:
    ret = False
    cmd = f'ping -W1 -c1 {SERVER1}'
    out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()
    match = search(b'[1].*, [1].*, [0]%.*,', out)
    if match is not None:
        ret = True
    return ret


def delete_content(fname: Union[str, bytes, int]) -> None:
    with open(fname, "w"):
        pass


def check_upd(local_chk: bool, verbose: bool) -> None:
    delete_content(tmplogfile)
    delete_content(logfile)
    tmp = open(tmplogfile, 'w')
    log = open(logfile, 'w')
    tmp.write(strftime('%a %b %d %H:%M:%S %Z %Y') + '\n')
    if not local_chk:
        # info('Start syncing overlays...') if verbose else None
        # system(f'sudo layman -SN >> {tmplogfile} > {DEVNULL}')
        # info('Layman Done') if verbose else None
        info('Start syncing portage...') if verbose else None
        debug(f'sudo eix-sync >> {tmplogfile} > {DEVNULL}') if verbose else None
        system(f'sudo eix-sync >> {tmplogfile} > {DEVNULL}')
        info('Sync Done.') if verbose else None

    info('Checking updates...') if verbose else None
    output = emerge('-pvNDu --color n @world'.split(), verbose, build=False)
    info('Updates checked') if verbose else None
    log.write(output.decode(encoding='utf-8'))
    tmp.close()
    log.close()

    # system('sudo /usr/local/sbin/tmerge.py 1G -pvNDu --with-bdeps=y --color n @world >> %s' % logfile)
    info('Creating log file...') if verbose else None
    debug(f'cat {logfile} >> {tmplogfile}') if verbose else None
    system(f'cat {logfile} >> {tmplogfile}')
    debug(f'cat {logfile} | genlop -pn >> {tmplogfile}') if verbose else None
    system(f'cat {logfile} | genlop -pn >> {tmplogfile}')
    info('Wrote to logs file') if verbose else None


# <=><=><=><=><=><=><=><=><=><=><=><=> tmerge <=><=><=><=><=><=><=><=><=><=><=><=>
def size_of_mounted_tmpfs(port_tmp_dir: str) -> int:
    df_cmd = run_cmd('df')
    match = search(r'(tmpfs\s*)(\d+)(\s*.*%s)' % port_tmp_dir, df_cmd.decode())
    if match is not None:
        return int(match.group(2))
    return 0


def remounttmpfs(size: str, verbose: bool, port_tmp_dir: str) -> None:
    info(f'Remounting {size} of memory to {port_tmp_dir}') if verbose else None
    debug(f'sudo umount -f {port_tmp_dir}') if verbose else None
    run_cmd(f'sudo umount -f {port_tmp_dir}')
    debug(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {port_tmp_dir}') if verbose else None
    run_cmd(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {port_tmp_dir}')


def run_cmd(cmd: str) -> bytes:
    out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()
    return out


def post_emerge(args: List[str], verbose: bool, return_code: bytes) -> None:
    pretend, world = check_emerge_opts(args)
    if len(return_code) is 0 and not pretend and world:
        info('Clearing emerge log') if verbose else None
        tmp = open(tmplogfile, 'w')
        log = open(logfile, 'w')
        log.write('Total: 0 packages, Size of downloads: 0 KiB')
        tmp.close()
        log.close()


def deep_clean(args: List[str], verbose: bool, return_code: bytes) -> None:
    pretend, world = check_emerge_opts(args)
    if len(return_code) is 0 and not pretend and world:
        out = emerge(['-pc'], verbose, build=False)
        info('Deep clean') if verbose else None
        debug(f'Details:{out.decode(encoding="utf-8")}') if verbose else None


def check_emerge_opts(args: List[str]) -> Tuple[bool, bool]:
    pretend = True
    world = False
    if 'p' not in args[0] or 'f' in args[0]:
        pretend = False
    if 'world' in ' '.join(args):
        world = True
    return pretend, world


def is_tmpfs_mounted(port_tmp_dir: str) -> bool:
    mount_cmd = run_cmd('mount')
    match = search(r'(tmpfs on\s+)(%s)(\s+type tmpfs)' % port_tmp_dir, mount_cmd.decode())
    if match is not None and match.group(2) == port_tmp_dir:
        return True
    else:
        return False


def is_portage_running() -> bool:
    running = run_cmd('pgrep -f /usr/bin/emerge')
    if running:
        return True
    else:
        return False


def convert2blocks(size: str) -> int:
    match = search(r'(?i)(\d+)([KMG])', size)
    if match.group(2).upper() == 'K':
        return int(match.group(1))
    if match.group(2).upper() == 'M':
        return int(match.group(1)) * 1024
    if match.group(2).upper() == 'G':
        return int(match.group(1)) * 1024 * 1024


def set_portage_tmpdir() -> None:
    if environ.get('PORTAGE_TMPDIR') is None:
        environ['PORTAGE_TMPDIR'] = PORTAGE_TMPDIR


if __name__ == '__main__':
    parser = ArgumentParser(description='Emerge in temporary RAM disk')
    parser.add_argument('-s', '--size', action='store', dest='size', default='4G', help='Size or RAM disk, default 4G')
    parser.add_argument('-l', '--check_local', action='store_true', dest='local', default=False, help='check locally')
    parser.add_argument('-d', '--deep_clean', action='store_true', dest='deep', default=False, help='no deep clean')
    parser.add_argument('-w', '--world', action='store_true', dest='world', default=False, help='run emerge -NDu @world')
    parser.add_argument('-r', '--pretend_world', action='store_true', dest='pretend_world', default=False, help='run emerge -pvNDu @world')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Show more data')
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
        if not is_tmpfs_mounted(PORTAGE_TMPDIR):
            mounttmpfs(opts.size, opts.verbose, PORTAGE_TMPDIR)
        elif size_of_mounted_tmpfs(PORTAGE_TMPDIR) != convert2blocks(opts.size):
            remounttmpfs(opts.size, opts.verbose, PORTAGE_TMPDIR)
        else:
            info('tmpfs is already mounted with requested size!') if opts.verbose else None

        if opts.action == 'emerge':
            rc = emerge(emerge_opts, opts.verbose, build=True)
            post_emerge(emerge_opts, opts.verbose, rc)
            if opts.deep:
                deep_clean(emerge_opts, opts.verbose, rc)
        elif opts.action == 'check':
            if ping_test() or opts.local:
                info('There is internet connecton') if opts.verbose else None
                check_upd(opts.local, opts.verbose)
            else:
                warning('No internet connection!\n') if opts.verbose else None
    else:
        info('emerge already running!') if opts.verbose else None
    unmounttmpfs(opts.size, opts.verbose, PORTAGE_TMPDIR)
