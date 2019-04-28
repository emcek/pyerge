#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from datetime import datetime
from re import search

from pyerge import emerge_logfile

__version__ = '0.3.0'


with open(emerge_logfile) as fd:
    for line in reversed(list(fd)):
        match = search(r'(\d+)(:\s===\sSync completed)', line)
        if match is not None:
            sync_time = match.group(1)
            print(datetime.fromtimestamp(int(sync_time)).strftime('%A %H:%M'))
            break
    else:
        print('Unknown')
