#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from datetime import datetime
from re import search

from pyerge import emerge_logfile, tmerge_logfile


def e_sync():
    with open(emerge_logfile) as fd:
        for line in reversed(list(fd)):
            match = search(r'(\d+)(:\s===\sSync completed)', line)
            if match is not None:
                sync_time = match.group(1)
                print(datetime.fromtimestamp(int(sync_time)).strftime('%A %H:%M'))
                break
        else:
            print('Unknown')


def e_dl():
    size = None

    with open(tmerge_logfile, 'r') as log:
        match = search(r'(Size of downloads:.)([0-9,]*\s[KMG]iB)', str(log.readlines()))
        if match is not None:
            size = match.group(2)

    if size == '0 KiB':
        size = 'None'
    elif not size:
        size = 'Calculating...'

    print(size)
