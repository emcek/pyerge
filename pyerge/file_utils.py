#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from datetime import datetime
from re import search, sub

from pyerge import emerge_logfile, tmerge_logfile, tmplogfile


def e_sync() -> str:
    """
    Fetch date of last sync form logs.

    :return: date as string
    :rtype: str
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
    :rtype: str
    """
    with open(tmerge_logfile, 'r') as log_file:
        for line in reversed(list(log_file)):
            match = search(r'(Size of downloads:.)([0-9,]*\s[KMG]iB)', line)
            if match is not None:
                size = match.group(2)
                break
        else:
            size = None

    if size == '0 KiB':
        size = 'None'
    elif not size:
        size = 'Calculating...'

    return size


def e_curr() -> str:
    """
    Get name of the current or last compiled package.

    :return: name of package with version
    :rtype: str
    """
    with open(emerge_logfile) as log_file:
        for line in reversed(list(log_file)):
            match = search(r'Compiling.*\((.*)::', line)
            if match is not None:
                pack = match.group(1)
                break
        else:
            pack = ''
    return pack


def e_eut() -> str:
    """
    Get estimated update time.

    :return: estimated update time
    :rtype: str
    """
    with open(tmplogfile) as log_file:
        for line in reversed(list(log_file)):
            match = search(r'Estimated update time:\s+(.*)\.', line)
            if match is not None:
                eut = match.group(1).replace(',', '')
                eut = sub(' minutes| minute', 'min', eut)
                eut = sub(' hours| hour', 'h', eut)
                break
        else:
            eut = 'Unknown'
    return eut
