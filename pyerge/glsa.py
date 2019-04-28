#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from argparse import ArgumentParser
from contextlib import closing
from re import match
from typing import List
from urllib.request import urlopen

from bs4 import BeautifulSoup
from pyerge import utils, __version__


def _collect_all_maching_entries(html: str, regex: str) -> List[str]:
    """
    Parse web page and find all matching tags.

    :param html: web page
    :param regex: regural expresion
    :return: list of strings
    """
    tmp_list = []
    soup = BeautifulSoup(html, 'html.parser')
    all_a_tags = soup.find_all('title')
    for tag in all_a_tags:
        found = match(regex, tag.text)
        if found:
            tmp_list.append(found.group(1))
    return tmp_list


def rss(webpage: str, regex: str, elements: int) -> List[str]:
    """
    Parse web page and find all matching tags.

    :param webpage: addres of web page
    :param regex: regural expresion
    :param elements: number of elements to return
    :return: list of strings
    """
    with closing(urlopen(webpage)) as rss_page:
        rss_html = rss_page.read().decode('UTF-8')
    all_versions = _collect_all_maching_entries(rss_html, regex)
    return all_versions[0:elements]


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
        out, err = utils.run_cmd(f'glsa-check -t {glsa_list}')
        if err == b'This system is not affected by any of the listed GLSAs\n':
            print("System is not affected by any of listed GLSAs")
        else:
            print(out.decode('UTF-8').strip())
    else:
        parser.print_help()
