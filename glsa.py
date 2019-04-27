#!/usr/bin/python3.6
from argparse import ArgumentParser
from contextlib import closing
from re import match
from shlex import split
from subprocess import Popen, PIPE
from typing import List, Tuple
from urllib.request import urlopen

from bs4 import BeautifulSoup

__author__ = 'emc'
__license__ = 'GPL'
__version__ = '0.3.0'


def _collect_all_maching_entries(html: str, regex: str) -> List[str]:
    tmp_list = []
    soup = BeautifulSoup(html, 'html.parser')
    all_a_tags = soup.find_all('title')
    for tag in all_a_tags:
        found = match(regex, tag.text)
        if found:
            tmp_list.append(found.group(1))
    return tmp_list


def rss(webpage: str, regex: str, elements: int) -> List[str]:
    with closing(urlopen(webpage)) as rss_page:
        rss_html = rss_page.read().decode('UTF-8')
    all_versions = _collect_all_maching_entries(rss_html, regex)
    return all_versions[0:elements]


def run_cmd(cmd: str) -> Tuple[bytes, bytes]:
    stdout, stderr = Popen(split(cmd), stdout=PIPE, stderr=PIPE).communicate()
    return stdout, stderr


if __name__ == '__main__':
    parser = ArgumentParser(description='Check and list GLSA easly')
    parser.add_argument('-e', '--elements', action='store', dest='elements', type=int, default='5', help='number of elements')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('action', help='list or test')
    opts, _ = parser.parse_known_args()

    if opts.action == 'list':
        print('\n'.join(rss(webpage='https://security.gentoo.org/glsa/feed.rss1',
                            regex=r'GLSA\s(\d{6}-\d{2}:\s.*)',
                            elements=opts.elements)))
    elif opts.action == 'test':
        glsa_list = ' '.join(rss(webpage='https://security.gentoo.org/glsa/feed.rss1',
                                 regex=r'GLSA\s(\d{6}-\d{2}):\s.*',
                                 elements=opts.elements))
        out, err = run_cmd(f'glsa-check -t {glsa_list}')
        if err == b'This system is not affected by any of the listed GLSAs\n':
            print("System is not affected by any of listed GLSAs")
        else:
            print(out.decode('UTF-8').strip())
    else:
        parser.print_help()
