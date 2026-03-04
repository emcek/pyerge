from argparse import ArgumentParser
from collections.abc import Iterator
from itertools import islice
from re import match
from urllib import request

from bs4 import BeautifulSoup

from pyerge import utils

GLSA_LIST_REGEX = r'GLSA\s(\d{6}-\d{2}:\s.*)'
GLSA_TEST_REGEX = r'GLSA\s(\d{6}-\d{2}):\s.*'
GLSA_RSS_FEED_URL = 'https://security.gentoo.org/glsa/feed.rss'


def _fetch_text(url: str, encoding: str = 'utf-8') -> str:
    """
    Fetch text content from a specified URL with the given encoding.

    This function opens a URL and retrieves its text content using the specified
    character encoding. It is commonly used to fetch data from web resources.

    param url: The URL to fetch the text content from.
    param encoding: The character encoding to decode the response. Defaults to 'utf-8'.

    return: Decoded text content retrieved from the specified URL.
    """
    with request.urlopen(url) as response:
        return response.read().decode(encoding)


def glsa_list(elements: int, feed_url: str = GLSA_RSS_FEED_URL) -> str:
    """
    List GLSAs with number and name as a string with new lines.

    :param elements: Number of elements
    :param feed_url: RSS feed URL
    :return: String with new lines
    """
    if elements <= 0:
        return ''
    feed_xml = _fetch_text(feed_url)
    entries = _collect_all_matching_entries(feed_xml, GLSA_LIST_REGEX)
    return '\n'.join(islice(entries, elements))


def glsa_test(elements: int, feed_url: str = GLSA_RSS_FEED_URL) -> str:
    """
    Test system against GLSAs.

    :param elements: Number of elements
    :param feed_url: RSS feed URL
    :return: String with a result
    """
    if elements <= 0:
        return ''
    feed_xml = _fetch_text(feed_url)
    entries = _collect_all_matching_entries(feed_xml, GLSA_TEST_REGEX)
    glsalist = ' '.join(islice(entries, elements))
    out, err = utils.run_cmd(f'glsa-check -t {glsalist}')
    if err == b'This system is not affected by any of the listed GLSAs\n':
        return 'System is not affected by any of listed GLSAs'
    return out.decode('utf-8').strip().replace('\n', ',')


def _collect_all_matching_entries(html: str, regex: str) -> Iterator[str]:
    """
    Parse a web page and find all matching tags.

    :param html: Web page
    :param regex: Regular expression
    :return: List of strings
    """
    soup = BeautifulSoup(html, 'xml')
    all_a_tags = soup.find_all('title')
    for tag in all_a_tags:
        if not tag.text:
            continue
        found = match(regex, tag.text)
        if found:
            yield found.group(1)


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
