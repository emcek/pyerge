#!/usr/bin/python3.6
from argparse import ArgumentParser
from logging import debug, basicConfig, warning, DEBUG, info
from os import system
from re import search
from shlex import split
from subprocess import Popen, PIPE
from time import strftime

from tmerge import mounttmpfs, unmounttmpfs, emerge

__author__ = 'emc'
__license__ = 'GPL'
__version__ = '0.3.0'

SERVER1 = '89.16.167.134'
SERVER2 = '85.17.140.211'
tmplogfile = '/var/log/portage/tmerge/tmp.emerge.log'
logfile = '/var/log/portage/tmerge/emerge.log'
DEVNULL = '/dev/null 2>&1'
basicConfig(format='%(asctime)s | %(levelname)s | %(message)s', level=DEBUG)


def test_ping():
    ret = False
    cmd = f'ping -W1 -c1 {SERVER1}'
    out, err = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()
    match = search(b'[1].*, [1].*, [0]%.*,', out)
    if match is not None:
        ret = True
    return ret


def delete_content(fname):
    with open(fname, "w"):
        pass


def check_upd(local_chk, verbose):
    delete_content(tmplogfile)
    delete_content(logfile)
    tmp = open(tmplogfile, 'w')
    log = open(logfile, 'w')
    tmp.write(strftime('%a %b %d %H:%M:%S %Z %Y') + '\n')
    if not local_chk:
        # if debug:
        #     print('Start syncing overlays...')
        # system(f'sudo layman -SN >> {tmplogfile} > {DEVNULL}')
        if verbose:
            # print('Layman Done')
            info('Start syncing portage...')
            debug(f'sudo eix-sync >> {tmplogfile} > {DEVNULL}')
        system(f'sudo eix-sync >> {tmplogfile} > {DEVNULL}')
        if verbose:
            info('Sync Done.')

    size = '1G'
    portage_tmpdir = '/var/tmp/portage'
    mounttmpfs(size, verbose, portage_tmpdir)
    if verbose:
        info('Checking updates...')
    output = emerge('-pvNDu --color n @world'.split(), verbose, build=False)
    if verbose:
        info('Updates checked')
    log.write(output.decode(encoding='UTF-8'))
    tmp.close()
    log.close()
    unmounttmpfs(size, verbose, portage_tmpdir)
    # system('sudo /usr/local/sbin/tmerge.py 1G -pvNDu --with-bdeps=y --color n @world >> %s' % logfile)
    if verbose:
        info('Creating log file...')
        debug(f'cat {logfile} >> {tmplogfile}')
    system(f'cat {logfile} >> {tmplogfile}')
    if verbose:
        debug(f'cat {logfile} | genlop -pn >> {tmplogfile}')
    system(f'cat {logfile} | genlop -pn >> {tmplogfile}')
    if verbose:
        info('Wrote to logs file')


def print_ok(msg):
    print('\u2713 ' + msg)


if __name__ == '__main__':
    parser = ArgumentParser(description='Check Portage Updates')
    parser.add_argument('-l', '--check_local', action='store_true', dest='local', default=False, help='check local')
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Show more data')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    opts = parser.parse_args()

    pingable = test_ping()
    if pingable or opts.local:
        if opts.verbose:
            # print_ok(msg='There is internet connecton')
            info('There is internet connecton')
        check_upd(opts.local, opts.verbose)
    else:
        if opts.verbose:
            warning('No internet connection!\n')
        exit()
