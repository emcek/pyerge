from argparse import Namespace
from logging import debug, info
from re import search
from time import strftime

from pyerge import DEVNULL, TMERGE_LOGFILE, TMPLOGFILE, utils


def emerge(arguments: list[str], build=True) -> tuple[bytes, bytes]:
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
        debug(f'RC: {return_code.decode("utf-8")}, stderr: {stderr.decode("utf-8")}')
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
        tmp.write(f"{strftime('%a %b %d %H:%M:%S %Z %Y')}\n")
        if not local_chk:
            info('Start syncing portage...')
            sync_cmd = f'sudo eix-sync >> {TMPLOGFILE} > {DEVNULL}'
            debug(sync_cmd)
            utils.run_cmd(cmd=sync_cmd, use_system=True)
        info('Checking updates...')
        world_args = '-pvNDu --color n --with-bdeps=y @world'.split()
        output, error = emerge(arguments=world_args, build=False)
        debug(f'stderr: {error.decode("utf-8")}')
        log.write(output.decode('utf-8'))
        log.write(error.decode('utf-8'))

    info('Creating log file...')
    cmd = f'cat {TMERGE_LOGFILE} >> {TMPLOGFILE}'
    debug(cmd)
    utils.run_cmd(cmd=cmd, use_system=True)
    cmd = f'cat {TMERGE_LOGFILE} | genlop -pn >> {TMPLOGFILE}'
    debug(cmd)
    utils.run_cmd(cmd=cmd, use_system=True)


# <=><=><=><=><=><=><=><=><=><=><=><=> tmerge <=><=><=><=><=><=><=><=><=><=><=><=>
def post_emerge(args: list[str], return_code: bytes) -> None:
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


def deep_clean(args: list[str], opts: Namespace, return_code: bytes) -> None:
    """
    Run deep clean after emerge.

    :param args:
    :param opts:
    :param return_code:
    """
    pretend, world = check_emerge_opts(args)
    if not int(return_code) and not pretend and world:
        output, error = emerge(arguments=['-pc'], build=False)
        info('Deep clean')
        info(f'output details:{output.decode("utf-8")}')
        debug(f'stderr details:{error.decode("utf-8")}')
        deep_run(opts, output)


def deep_run(opts: Namespace, output: bytes) -> None:
    """
    Run deep clean emegre without gent0o sources.

    :param opts:
    :param output:
    """
    if not opts.deep_run:
        return
    match = search(r'All selected packages:\s(.*)\n', output.decode('utf-8'))
    if match is None:
        return
    packages_to_clean = [package for package in match.group(1).split(' ') if 'gentoo-sources' not in package]
    if not packages_to_clean:
        info('Nothing to clean')
        debug(f'All packages: {match.group(1)}')
        return
    debug(f'Cleaning {len(packages_to_clean)} packages')
    emerge(arguments=['-c', *packages_to_clean], build=True)


def check_emerge_opts(args: list[str]) -> tuple[bool, bool]:
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


def run_emerge(emerge_opts: list[str], opts: Namespace) -> tuple[bytes, bytes]:
    """
    Run update of system.

    :param emerge_opts: list of arguments for emege
    :param opts: cli arguments
    """
    if opts.action != 'emerge' or not opts.online:
        return b'', b''

    is_world_update = bool(opts.world or opts.pretend_world)
    wants_deep_clean = bool(opts.deep_print or opts.deep_run)

    return_code, stderr = emerge(arguments=emerge_opts, build=True)

    if is_world_update:
        post_emerge(emerge_opts, return_code)
        if wants_deep_clean:
            deep_clean(emerge_opts, opts, return_code)

    return return_code, stderr


def run_check(opts: Namespace) -> None:
    """
    Run checking system updates.

    :param opts: cli arguments
    """
    if opts.action == 'check' and (opts.online or opts.local):
        check_upd(opts.local)


def run_live(opts: Namespace) -> tuple[bytes, bytes]:
    """
    Emerge live packages with smart-live-rebuild.

    :param opts: cli arguments
    :return:
    """
    if not (opts.live and opts.online):
        return b'', b''

    cmd_parts: list[str] = ['smart-live-rebuild', '--no-color']
    if opts.action == 'check':
        cmd_parts.append('--pretend')

    cmd = ' '.join(cmd_parts)
    info(f'running: {cmd}')

    return_code, stderr = utils.run_cmd(cmd, use_system=True)
    debug(f'RC: {return_code.decode("utf-8")}, stderr: {stderr.decode("utf-8")}')
    return return_code, stderr
