#!/usr/bin/python3.6
from re import search
from shlex import split
from subprocess import Popen, PIPE

__version__ = '0.3'


def run_cmd(cmd: str) -> bytes:
    out, _ = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()
    return out


if __name__ == '__main__':
    output = run_cmd('genlop -cn').decode()
    if search(r'Error.*no working merge found', output):
        print('Unknown')
        exit()

    match = search(r'ETA:\s(.*)\.', output)
    if match:
        print(match.group(1))
