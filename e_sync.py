#!/usr/bin/python3.6
from datetime import datetime
from re import search

__author__ = 'emc'
__license__ = 'GPL'
__version__ = '0.3.0'

logfile = '/var/log/emerge.log'

with open(logfile) as fd:
    for line in reversed(list(fd)):
        match = search(r'(\d+)(:\s===\sSync completed)', line)
        if match is not None:
            sync_time = match.group(1)
            print(datetime.fromtimestamp(int(sync_time)).strftime('%A %H:%M'))
            break
    else:
        print('Unknown')

