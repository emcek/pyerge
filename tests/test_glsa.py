from unittest import mock

from pytest import mark

date1 = '201904-23'
date2 = '201904-22'
date3 = '201904-13'
date4 = '201904-14'
vulnerabilities = f'{date1}: GLib: Multiple vulnerabilities'
escalation = f'{date2}: OpenDKIM: Root privilege escalation'


def test_glsa_list():
    from pyerge.glsa import glsa_list
    from argparse import Namespace
    with mock.patch('pyerge.glsa._rss') as rss_mock:
        rss_mock.return_value = [vulnerabilities, escalation]
        assert glsa_list(Namespace(elements=2)) == f'{vulnerabilities}\n{escalation}'


def test_glsa_test_system_not_affected():
    from pyerge.glsa import glsa_test
    from argparse import Namespace
    with mock.patch('pyerge.glsa.utils') as utils_mock:
        with mock.patch('pyerge.glsa._rss') as rss_mock:
            rss_mock.return_value = [date1, date2]
            utils_mock.run_cmd.return_value = b'', b'This system is not affected by any of the listed GLSAs\n'
            assert glsa_test(Namespace(elements=2)) == 'System is not affected by any of listed GLSAs'


def test_glsa_test_system_affected():
    from pyerge.glsa import glsa_test
    from argparse import Namespace
    with mock.patch('pyerge.glsa.utils') as utils_mock:
        with mock.patch('pyerge.glsa._rss') as rss_mock:
            rss_mock.return_value = [date1, date2, date3]
            utils_mock.run_cmd.return_value = b'201904-13\n201904-14\n', b'This system is affected by the following GLSAs:\n'
            assert glsa_test(Namespace(elements=2)) == f'{date3},{date4}'


def test_rss():
    from pyerge.glsa import _rss
    html = b'<?xml version="1.0" encoding="UTF-8"?>\n<rdf:RDF xmlns="http://purl.org/rss/1.0/"\n  ' \
           b'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n  ' \
           b'xmlns:content="http://purl.org/rss/1.0/modules/content/"\n  ' \
           b'xmlns:dc="http://purl.org/dc/elements/1.1/"\n  ' \
           b'xmlns:image="http://purl.org/rss/1.0/modules/image/"\n  ' \
           b'xmlns:slash="http://purl.org/rss/1.0/modules/slash/"\n  ' \
           b'xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"\n  ' \
           b'xmlns:taxo="http://purl.org/rss/1.0/modules/taxonomy/"\n  ' \
           b'xmlns:trackback="http://madskills.com/public/xml/rss/module/trackback/">\n' \
           b'<channel rdf:about="https://security.gentoo.org/glsa">\n    ' \
           b'<title>Gentoo Linux security advisories</title>\n    ' \
           b'<link>https://security.gentoo.org/glsa</link>\n    ' \
           b'<description>This feed contains new Gentoo Linux security advisories. ' \
           b'Contact security@gentoo.org with questions.</description>\n' \
           b'<items>\n      <rdf:Seq>\n' \
           b'<rdf:li resource="https://security.gentoo.org/glsa/201904-25"/>\n' \
           b'<rdf:li resource="https://security.gentoo.org/glsa/201904-24"/>\n' \
           b'<rdf:li resource="https://security.gentoo.org/glsa/201904-23"/>\n' \
           b'</items>\n    <dc:date>2019-04-24T00:00:00+00:00</dc:date>\n  </channel>\n' \
           b'<item rdf:about="https://security.gentoo.org/glsa/201904-25">\n    ' \
           b'<title>GLSA 201904-25: QEMU: Multiple vulnerabilities</title>\n    ' \
           b'<link>https://security.gentoo.org/glsa/201904-25</link>\n    ' \
           b'<dc:date>2019-04-24T00:00:00+00:00</dc:date>\n  </item>\n' \
           b'<item rdf:about="https://security.gentoo.org/glsa/201904-24">\n    ' \
           b'<title>GLSA 201904-24: Ming: Multiple vulnerabilities</title>\n    ' \
           b'<link>https://security.gentoo.org/glsa/201904-24</link>\n    ' \
           b'<dc:date>2019-04-24T00:00:00+00:00</dc:date>\n  </item>\n' \
           b'<item rdf:about="https://security.gentoo.org/glsa/201904-23">\n    ' \
           b'<title>GLSA 201904-23: GLib: Multiple vulnerabilities</title>\n    ' \
           b'<link>https://security.gentoo.org/glsa/201904-23</link>\n    ' \
           b'<dc:date>2019-04-22T00:00:00+00:00</dc:date>\n  </item>\n' \
           b'</rdf:RDF>'

    with mock.patch('pyerge.glsa.urlopen') as urlopen_mock:
        with mock.patch('pyerge.glsa._collect_all_maching_entries') as collect_all_mock:
            urlopen_mock.return_value.read.return_value = html
            collect_all_mock.return_value = ['201904-25', '201904-24', '201904-23']
            assert _rss(r'GLSA\s(\d{6}-\d{2}):\s.*', 2) == ['201904-25', '201904-24']


@mark.parametrize('regex, result', [(r'GLSA\s(\d{6}-\d{2}):\s.*', [date1, date2]),
                                    (r'GLSA\s(\d{6}-\d{2}:\s.*)', [vulnerabilities, escalation])])
def test_collect_all_maching_entries(regex, result):
    from pyerge.glsa import _collect_all_maching_entries
    html = """
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns="http://purl.org/rss/1.0/"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:image="http://purl.org/rss/1.0/modules/image/"
  xmlns:slash="http://purl.org/rss/1.0/modules/slash/"
  xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
  xmlns:taxo="http://purl.org/rss/1.0/modules/taxonomy/"
  xmlns:trackback="http://madskills.com/public/xml/rss/module/trackback/">
  <channel rdf:about="https://security.gentoo.org/glsa">
    <title>Gentoo Linux security advisories</title>
    <link>https://security.gentoo.org/glsa</link>
    <description>This feed contains new Gentoo Linux security advisories. Contact security@gentoo.org with questions.</description>
    <items>
      <rdf:Seq>
        <rdf:li resource="https://security.gentoo.org/glsa/201904-23"/>
        <rdf:li resource="https://security.gentoo.org/glsa/201904-22"/>
      </rdf:Seq>
    </items>
    <dc:date>2019-04-24T00:00:00+00:00</dc:date>
  </channel>
  <item rdf:about="https://security.gentoo.org/glsa/201904-23">
    <title>GLSA 201904-23: GLib: Multiple vulnerabilities</title>
    <link>https://security.gentoo.org/glsa/201904-23</link>
    <dc:date>2019-04-22T00:00:00+00:00</dc:date>
  </item>
  <item rdf:about="https://security.gentoo.org/glsa/201904-22">
    <title>GLSA 201904-22: OpenDKIM: Root privilege escalation</title>
    <link>https://security.gentoo.org/glsa/201904-22</link>
    <dc:date>2019-04-22T00:00:00+00:00</dc:date>
  </item>
</rdf:RDF>
"""
    assert _collect_all_maching_entries(html, regex) == result
