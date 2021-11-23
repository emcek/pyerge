from argparse import ArgumentParser
from re import match
from sys import modules
from typing import List
from urllib import request, error

from bs4 import BeautifulSoup

from pyerge import utils


def glsa_list(elements: int) -> str:
    """
    List GLSAs with number and name as string with new lines.

    :param elements: number of elements
    :return: string with new lines
    """
    return '\n'.join(_rss(regex=r'GLSA\s(\d{6}-\d{2}:\s.*)', elements=elements))


def glsa_test(elements: int) -> str:
    """
    Test system against GLSAs.

    :param elements: number of elements
    :return: string with result
    """
    glsalist = ' '.join(_rss(regex=r'GLSA\s(\d{6}-\d{2}):\s.*', elements=elements))
    out, err = utils.run_cmd(f'glsa-check -t {glsalist}')
    if err == b'This system is not affected by any of the listed GLSAs\n':
        return 'System is not affected by any of listed GLSAs'
    return out.decode('utf-8').strip().replace('\n', ',')


def _rss(regex: str, elements: int) -> List[str]:
    """
    Parse web page and find all matching tags.

    :param regex: regural expresion
    :param elements: number of elements to return
    :return: list of strings
    """
    with request.urlopen('https://security.gentoo.org/glsa/feed.rss1') as rss_page:  # nosec
        rss_html = rss_page.read().decode('utf-8')
    all_versions = _collect_all_maching_entries(rss_html, regex)
    return all_versions[0:elements]


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


def run_glsa():
    """Run GLSA module to test or to list."""
    parser = ArgumentParser(description='Check and list GLSA easly')
    parser.add_argument('action', help='list or test')
    parser.add_argument('-e', '--elements', action='store', dest='elements', type=int, default='5', help='number of elements')
    args = parser.parse_args()
    try:
        print(getattr(modules['pyerge.glsa'], f'glsa_{args.action}')(args.elements))
    except (AttributeError, KeyError, error.HTTPError) as err:
        print(f'{err}')
