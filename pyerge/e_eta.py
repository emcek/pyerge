#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from re import search

from pyerge import utils

__version__ = '0.3'


if __name__ == '__main__':
    output, _ = utils.run_cmd('genlop -cn')
    if search(r'Error.*no working merge found', output.decode()):
        print('Unknown')
        exit()

    match = search(r'ETA:\s(.*)\.', output.decode())
    if match:
        print(match.group(1))
