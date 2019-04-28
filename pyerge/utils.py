from logging import info, debug
from re import search
from shlex import split
from subprocess import Popen, PIPE
from typing import Union, Tuple

from pyerge import SERVER1


def mounttmpfs(size: str, verbose: bool, port_tmp_dir: str) -> None:
    if verbose:
        info(f'Mounting {size} of memory to {port_tmp_dir}')
        debug(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {port_tmp_dir}')
    run_cmd(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {port_tmp_dir}')


def unmounttmpfs(size: str, verbose: bool, port_tmp_dir: str) -> None:
    if verbose:
        info(f'Unmounting {size} of memory from {port_tmp_dir}')
        debug(f'sudo umount -f {port_tmp_dir}')
    run_cmd(f'sudo umount -f {port_tmp_dir}')


def remounttmpfs(size: str, verbose: bool, port_tmp_dir: str) -> None:
    if verbose:
        info(f'Remounting {size} of memory to {port_tmp_dir}')
        debug(f'sudo umount -f {port_tmp_dir}')
    run_cmd(f'sudo umount -f {port_tmp_dir}')
    if verbose:
        debug(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {port_tmp_dir}')
    run_cmd(f'sudo mount -t tmpfs -o size={size},nr_inodes=1M tmpfs {port_tmp_dir}')


def run_cmd(cmd: str) -> Tuple[bytes, bytes]:
    out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()
    return out, err


def is_internet_connected() -> bool:
    ret = False
    cmd, _ = run_cmd(f'ping -W1 -c1 {SERVER1}')
    match = search(b'[1].*, [1].*, [0]%.*,', cmd)
    if match is not None:
        ret = True
    return ret


def size_of_mounted_tmpfs(port_tmp_dir: str) -> int:
    df_cmd, _ = run_cmd('df')
    match = search(r'(tmpfs\s*)(\d+)(\s*.*%s)' % port_tmp_dir, df_cmd.decode())
    if match is not None:
        return int(match.group(2))
    return 0


def is_tmpfs_mounted(port_tmp_dir: str) -> bool:
    mount_cmd, _ = run_cmd('mount')
    match = search(r'(tmpfs on\s+)(%s)(\s+type tmpfs)' % port_tmp_dir, mount_cmd.decode())
    if match is not None and match.group(2) == port_tmp_dir:
        return True
    else:
        return False


def convert2blocks(size: str) -> int:
    try:
        return int(float(size))
    except ValueError:
        pass
    match = search(r'(?i)(\d+)([KMG])', size)
    if match.group(2).upper() == 'K':
        # todo: add handling of floting point
        return int(match.group(1))
    if match.group(2).upper() == 'M':
        return int(match.group(1)) * 1024
    if match.group(2).upper() == 'G':
        return int(match.group(1)) * 1024 * 1024


def delete_content(fname: Union[str, bytes, int]) -> None:
    with open(fname, 'w'):
        pass
