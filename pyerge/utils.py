"""Various tools to emerge and to show status for conky."""
from argparse import Namespace
from logging import warning, info, debug
from os import system, environ
from re import search
from shlex import split
from subprocess import Popen, PIPE  # nosec
from typing import Union, Tuple

from pyerge import server, portage_tmpdir


def run_cmd(cmd: str, use_system=False) -> Tuple[bytes, bytes]:
    """
    Run any system command.

    If use_system is set cmd is run via os.system and function
    return RC from comand as bytes and b''.
    If use_system is not set (default) cmd is run via subprocess.Popen and
    function return cmd stdout and stderr as bytes.

    :param cmd: command string
    :param use_system: os.system use insted of subprocess
    :return: tuple of bytes with output and error
    """
    if use_system:
        ret_code = system(cmd)  # nosec
        out, err = str(ret_code).encode('utf-8'), b''
    else:
        out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()  # nosec
    return out, err


def mounttmpfs(size: str, verbose: int) -> None:
    """
    Mount directory with size as tmp file system in RAM.

    :param size: with unit K, M, G
    :param verbose: be verbose
    """
    if verbose:
        info(f'Mounting {size} of memory to {portage_tmpdir}')
    if verbose > 1:
        debug(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {portage_tmpdir}')
    run_cmd(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {portage_tmpdir}')


def unmounttmpfs(opts: Namespace) -> None:
    """
    Unmount directory from RAM.

    :param opts: cli arguments
    """
    if not opts.action == 'check' and (not opts.local or not opts.pretend_world):
        if opts.verbose:
            info(f'Unmounting {opts.size} of memory from {portage_tmpdir}')
        if opts.verbose > 1:
            debug(f'sudo umount -f {portage_tmpdir}')
        run_cmd(f'sudo umount -f {portage_tmpdir}')


def remounttmpfs(size: str, verbose: int) -> None:
    """
    Re-mount directory with size as tmp file system in RAM.

    :param size: with unit K, M, G
    :param verbose: be verbose
    """
    if verbose:
        info(f'Remounting {size} of memory to {portage_tmpdir}')
    if verbose > 1:
        debug(f'sudo umount -f {portage_tmpdir}')
    run_cmd(f'sudo umount -f {portage_tmpdir}')
    if verbose > 1:
        debug(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {portage_tmpdir}')
    run_cmd(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {portage_tmpdir}')


def is_internet_connected(verbose: int) -> bool:
    """
    Check if there is connection to internet.

    :param verbose: be verbose
    :return: True is connected, False otherwise
    """
    cmd, _ = run_cmd(f'ping -W1 -c1 {server}')
    match = search(b'[1].*, [1].*, [0]%.*,', cmd)
    if match is not None:
        if verbose:
            info('There is internet connecton or not needed')
        return True
    warning('No internet connection!')
    return False


def size_of_mounted_tmpfs() -> int:
    """
    Return size of mounted directory.

    :return: size in bytes as intiger
    """
    df_cmd, _ = run_cmd('df')
    match = search(r'(tmpfs\s*)(\d+)(\s*.*%s)' % portage_tmpdir, df_cmd.decode('utf-8'))
    if match is not None:
        return int(match.group(2))
    return 0


def is_tmpfs_mounted() -> bool:
    """
    Check if portage temp dir is mounted.

    :return: True is mounted, False otherwise
    """
    mount_cmd, _ = run_cmd('mount')
    match = search(r'(tmpfs on\s+)(%s)(\s+type tmpfs)' % portage_tmpdir, mount_cmd.decode('utf-8'))
    return bool(match is not None and match.group(2) == portage_tmpdir)


def convert2blocks(size: str) -> int:
    """
    Convert size with unit into system blocks (used in i.e. df/mounts commands).

    :param size: with units K, M, G
    :return: size in kB
    """
    try:
        return int(float(size))
    except ValueError as err:
        debug(f'Size: {size} Exception: {err}')
    match = search(r'(?i)(\d+)([KMG])', size)
    if match.group(2).upper() == 'K':
        return int(match.group(1))
    if match.group(2).upper() == 'M':
        return int(match.group(1)) * 1024
    if match.group(2).upper() == 'G':
        return int(match.group(1)) * 1024 * 1024


def delete_content(fname: Union[str, bytes, int]) -> None:
    """
    Clean-up file content.

    :param fname: path to file as string
    """
    with open(fname, 'w'):
        pass


def set_portage_tmpdir() -> str:
    """Set system variable."""
    if not environ.get('PORTAGE_TMPDIR', ''):
        environ['PORTAGE_TMPDIR'] = portage_tmpdir
    return environ['PORTAGE_TMPDIR']


def e_eta() -> str:
    """
    Get estimated time of compilation of current package.

    :return: time until compilation ends
    :rtype: str
    """
    output, _ = run_cmd('genlop -cn')
    out = output.decode('utf-8')
    eta = ''
    if search(r'Error.*no working merge found', out):
        eta = 'Unknown'

    match = search(r'ETA:\s(.*)\.', out)
    if match is not None:
        eta = match.group(1)
    return eta


def handling_mounting(opts: Namespace) -> None:
    """
    Handling mounting temporary file fistem with requestes size.

    :param opts: cli arguments
    """
    if not opts.action == 'check' and (not opts.local or not opts.pretend_world):
        if not is_tmpfs_mounted():
            mounttmpfs(opts.size, opts.verbose)
        elif size_of_mounted_tmpfs() != convert2blocks(opts.size):
            remounttmpfs(opts.size, opts.verbose)
        else:
            if opts.verbose:
                info('tmpfs is already mounted with requested size!')
