#!/usr/bin/python3.6
from re import search

from pyerge import logfile

__version__ = '0.3'

size = None

with open(logfile, 'r') as log:
    match = search(r'(Size of downloads:.)([0-9,]*\s[KMG]iB)', str(log.readlines()))
    if match is not None:
        size = match.group(2)

if size == '0 KiB':
    size = 'None'
elif not size:
    size = 'Calculating...'

print(size)
