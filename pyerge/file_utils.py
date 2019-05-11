#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from datetime import datetime
from re import search

from pyerge import emerge_logfile, tmerge_logfile


def e_sync() -> str:
    """
    Fetch date of last sync form logs.

    :return: date as string
    """
    with open(emerge_logfile) as log_file:
        for line in reversed(list(log_file)):
            match = search(r'(\d+)(:\s===\sSync completed)', line)
            if match is not None:
                sync_time = match.group(1)
                break
        else:
            return 'Unknown'
    return datetime.fromtimestamp(int(sync_time)).strftime('%A %H:%M')


def e_dl() -> str:
    """
    Fetch size of archives to be download for next system update.

    :return: date as string
    """
    size = None

    with open(tmerge_logfile, 'r') as log:
        match = search(r'(Size of downloads:.)([0-9,]*\s[KMG]iB)', str(log.readlines()))
        if match is not None:
            size = match.group(2)

    if size == '0 KiB':
        size = 'None'
    elif not size:
        size = 'Calculating...'

    return size
