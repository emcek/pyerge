#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from re import search

from pyerge import tmerge_logfile

__version__ = '0.3'

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
