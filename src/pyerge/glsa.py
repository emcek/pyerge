from argparse import ArgumentParser
from re import match
from urllib import request

from bs4 import BeautifulSoup

from pyerge import utils

GLSA_LIST_REGEX = r'GLSA\s(\d{6}-\d{2}:\s.*)'
GLSA_TEST_REGEX = r'GLSA\s(\d{6}-\d{2}):\s.*'


def glsa_list(elements: int) -> str:
    """
    List GLSAs with number and name as a string with new lines.

    :param elements: Number of elements
    :return: String with new lines
    """
    return '\n'.join(_rss(regex=GLSA_LIST_REGEX, elements=elements))


def glsa_test(elements: int) -> str:
    """
    Test system against GLSAs.

    :param elements: Number of elements
    :return: String with a result
    """
    glsalist = ' '.join(_rss(regex=GLSA_TEST_REGEX, elements=elements))
    out, err = utils.run_cmd(f'glsa-check -t {glsalist}')
    if err == b'This system is not affected by any of the listed GLSAs\n':
        return 'System is not affected by any of listed GLSAs'
    return out.decode('utf-8').strip().replace('\n', ',')


def _rss(regex: str, elements: int) -> list[str]:
    """
    Parse a web page and find all matching tags.

    :param regex: Regular expression
    :param elements: Number of elements to return
    :return: A list of strings
    """
    with request.urlopen('https://security.gentoo.org/glsa/feed.rss') as rss_page:
        rss_html = rss_page.read().decode('utf-8')
    all_versions = _collect_all_matching_entries(rss_html, regex)
    return all_versions[0:elements]


def _collect_all_matching_entries(html: str, regex: str) -> list[str]:
    """
    Parse a web page and find all matching tags.

    :param html: Web page
    :param regex: Regular expression
    :return: List of strings
    """
    tmp_list = []
    soup = BeautifulSoup(html, 'xml')
    all_a_tags = soup.find_all('title')
    for tag in all_a_tags:
        found = match(regex, tag.text)
        if found:
            tmp_list.append(found.group(1))
    return tmp_list


def run_glsa() -> None:
    """Run GLSA module to test or to list."""
    parser = ArgumentParser(description='Check and list GLSA easily')
    parser.add_argument('action', help='list or test')
    parser.add_argument('-e', '--elements', action='store', dest='elements', type=int, default='5', help='number of elements')
    args = parser.parse_args()

    if args.action == 'list':
        print(glsa_list(args.elements))
    elif args.action == 'test':
        print(glsa_test(args.elements))
