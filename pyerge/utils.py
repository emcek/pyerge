from argparse import Namespace
from logging import debug, info, warning
from os import environ, system
from re import search
from shlex import split
from subprocess import PIPE, Popen  # nosec
from typing import Tuple, Union

from pyerge import PORTAGE_TMPDIR


def run_cmd(cmd: str, use_system=False) -> Tuple[bytes, bytes]:
    """
    Run any system command.

    When use_system is set cmd is run via "os.system" and function
    return RC from comand as bytes and b''.
    When use_system is not set (default) cmd is run via subprocess.Popen and
    function return cmd stdout and stderr as bytes.

    :param cmd: command string
    :param use_system: "os.system" use insted of subprocess
    :return: tuple of bytes with output and error
    """
    if use_system:
        ret_code = system(cmd)  # nosec
        out, err = str(ret_code).encode('utf-8'), b''
    else:
        out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()  # nosec
    return out, err


def mount_device(opts: Namespace) -> None:
    """
    Mount directory with size as tmp file system in RAM or linu device.

    :param opts: cli arguments
    """
    if opts.dev == 'tmpfs':
        info(f'Mounting {opts.size} of memory to {PORTAGE_TMPDIR}')
        cmd = f'sudo mount -t tmpfs -o size={opts.size},nr_inodes=1M tmpfs {PORTAGE_TMPDIR}'
    else:
        info(f'Mounting {opts.dev} as {PORTAGE_TMPDIR}')
        cmd = f'sudo mount {opts.dev} {PORTAGE_TMPDIR}'
    debug(cmd)
    run_cmd(cmd)


def unmount_device(opts: Namespace) -> None:
    """
    Unmount directory from RAM or linux device.

    :param opts: cli arguments
    """
    if not opts.action == 'check' and (not opts.local or not opts.pretend_world):
        if opts.dev == 'tmpfs':
            info(f'Unmounting {opts.size} of memory from {PORTAGE_TMPDIR}')
        else:
            info(f'Unmounting {opts.dev} from {PORTAGE_TMPDIR}')
        debug(f'sudo umount -f {PORTAGE_TMPDIR}')
        run_cmd(f'sudo umount -f {PORTAGE_TMPDIR}')


def remount_tmpfs(opts: Namespace) -> None:
    """
    Re-mount directory with size as tmp file system in RAM.

    :param opts: cli arguments
    """
    info(f'Remounting {opts.size} of memory to {PORTAGE_TMPDIR}')
    debug(f'sudo umount -f {PORTAGE_TMPDIR}')
    run_cmd(f'sudo umount -f {PORTAGE_TMPDIR}')
    mount_device(opts)


def is_internet_connected() -> bool:
    """
    Check if there is connection to internet.

    :return: True is connected, False otherwise
    """
    cmd, _ = run_cmd('ping -W1 -c1 89.16.167.134')
    match = search(b'[1].*, [1].*, [0]%.*,', cmd)
    if match is not None:
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
    match = search(rf'(tmpfs\s*)(\d+)(\s*.*{PORTAGE_TMPDIR})', df_cmd.decode('utf-8'))
    if match is not None:
        return int(match.group(2))
    return 0


def is_device_mounted(dev='tmpfs') -> bool:
    """
    Check if Linux DEV is mounted.

    :param dev: linux dev name
    :return: True is mounted, False otherwise
    """
    mount_cmd, _ = run_cmd('mount')
    match = search(rf'({dev} on\s+)({PORTAGE_TMPDIR})(\s+type\s)', mount_cmd.decode('utf-8'))
    return bool(match is not None and match.group(2) == PORTAGE_TMPDIR)


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
    regex = search(r'(?i)(\d+)([KMG])', size)
    map_dict = {'K': 1, 'M': 1024, 'G': 1024 * 1024}
    return int(regex.group(1)) * map_dict[regex.group(2).upper()]  # type: ignore


def delete_content(fname: Union[str, bytes, int]) -> None:
    """
    Clean-up file content.

    :param fname: path to file as string
    """
    with open(file=fname, mode='w', encoding='utf-8'):
        pass


def set_portage_tmpdir() -> str:
    """Set system variable."""
    if not environ.get('PORTAGE_TMPDIR', ''):
        environ['PORTAGE_TMPDIR'] = PORTAGE_TMPDIR
    return environ['PORTAGE_TMPDIR']


def handling_mounting(opts: Namespace) -> None:
    """
    Handling mounting temporary file fistem with requestes size.

    :param opts: cli arguments
    """
    if not opts.action == 'check' and (not opts.local or not opts.pretend_world):
        if not is_device_mounted(dev=opts.dev):
            mount_device(opts)
        elif opts.dev == 'tmpfs' and size_of_mounted_tmpfs() != convert2blocks(opts.size):
            remount_tmpfs(opts)
        else:
            info('dev/tmpfs is already mounted with requested size!')
