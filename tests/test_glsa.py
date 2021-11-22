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
    with mock.patch('pyerge.glsa._rss') as rss_mock:
        rss_mock.return_value = [vulnerabilities, escalation]
        assert glsa_list(elements=2) == f'{vulnerabilities}\n{escalation}'


def test_glsa_test_system_not_affected():
    from pyerge.glsa import glsa_test
    with mock.patch('pyerge.glsa.utils') as utils_mock:
        with mock.patch('pyerge.glsa._rss') as rss_mock:
            rss_mock.return_value = [date1, date2]
            utils_mock.run_cmd.return_value = b'', b'This system is not affected by any of the listed GLSAs\n'
            assert glsa_test(elements=2) == 'System is not affected by any of listed GLSAs'


def test_glsa_test_system_affected():
    from pyerge.glsa import glsa_test
    with mock.patch('pyerge.glsa.utils') as utils_mock:
        with mock.patch('pyerge.glsa._rss') as rss_mock:
            rss_mock.return_value = [date1, date2, date3]
            utils_mock.run_cmd.return_value = b'201904-13\n201904-14\n', b'This system is affected by the following GLSAs:\n'
            assert glsa_test(elements=2) == f'{date3},{date4}'


def test_rss(orginal_html_xml):
    from pyerge.glsa import _rss
    with mock.patch('pyerge.glsa.request') as urlopen_mock:
        with mock.patch('pyerge.glsa._collect_all_maching_entries') as collect_all_mock:
            urlopen_mock.return_value.read.return_value = orginal_html_xml
            collect_all_mock.return_value = ['201904-25', '201904-24', '201904-23']
            assert _rss(r'GLSA\s(\d{6}-\d{2}):\s.*', 2) == ['201904-25', '201904-24']


@mark.parametrize('regex, result', [(r'GLSA\s(\d{6}-\d{2}):\s.*', [date1, date2]),
                                    (r'GLSA\s(\d{6}-\d{2}:\s.*)', [vulnerabilities, escalation])])
def test_collect_all_maching_entries(regex, result, html_xlm_as_str):
    from pyerge.glsa import _collect_all_maching_entries
    assert _collect_all_maching_entries(html_xlm_as_str, regex) == result
