#!/usr/bin/python3.6
"""Various tools to emerge and to show status for conky."""
from argparse import Namespace
from logging import debug
from re import match
from sys import modules
from typing import List
from urllib.request import urlopen

from bs4 import BeautifulSoup

from pyerge import utils, glsa_webpage


def glsa_list(opts: Namespace) -> str:
    """
    List GLSAs with number and name as string with new lines.

    :param opts: cli arguments
    :return: string with new lines
    """
    return '\n'.join(_rss(regex=r'GLSA\s(\d{6}-\d{2}:\s.*)', elements=opts.elements))


def glsa_test(opts: Namespace) -> str:
    """
    Test system against GLSAs.

    :param opts: cli arguments
    :return: string with result
    """
    glsalist = ' '.join(_rss(regex=r'GLSA\s(\d{6}-\d{2}):\s.*', elements=opts.elements))
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
    with urlopen(glsa_webpage) as rss_page:  # nosec
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


def run_glsa(opts: Namespace) -> str:
    """
    Run GLSA module to test or to list.

    :param opts: cli arguments
    :return: result of glsa action
    """
    if opts.online:
        try:
            return getattr(modules['__main__'], opts.action)(opts)
        except AttributeError as err:
            debug(f'Options: {opts} Exception: {err}')
            return ''
