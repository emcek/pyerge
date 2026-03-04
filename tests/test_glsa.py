from unittest import mock

from pytest import mark

from pyerge.glsa import GLSA_LIST_REGEX, GLSA_TEST_REGEX

all_dates = ['202601-05', '202601-04', '202601-03', '202601-02', '202601-01', '202512-01', '202511-07', '202511-06',
             '202511-05', '202511-04', '202511-03', '202511-02', '202511-01', '202509-08', '202509-07', '202509-06',
             '202509-05', '202509-04', '202509-03', '202509-02', '202509-01', '202508-06', '202508-05', '202508-04',
             '202508-03', '202508-02', '202508-01', '202507-10', '202507-09', '202507-08', '202507-07', '202507-06',
             '202507-05', '202507-04', '202507-03', '202507-02', '202507-01', '202506-13', '202506-12', '202506-11',
             '202506-10', '202506-09', '202506-08', '202506-07', '202506-06', '202506-05', '202506-04', '202506-03',
             '202506-02', '202506-01']
all_vuls = ['202601-05: Commons-BeanUtils: Arbitary Code Execution', '202601-04: Asterisk: Multiple Vulnerabilities',
            '202601-03: GIMP: Arbitrary Code Execution', '202601-02: Vim, gVim: Multiple Vulnerabilities',
            '202601-01: inetutils: Remote Code Execution', '202512-01: GnuPG: Arbitrary Code Execution',
            '202511-07: librnp: Weak random number generation', '202511-06: libpng: Multiple vulnerabilities',
            '202511-05: redict, redis: Multiple Vulnerabilities',
            '202511-04: Chromium, Google Chrome, Microsoft Edge. Opera: Multiple Vulnerabilities',
            '202511-03: qtsvg: Multiple Vulnerabilities', '202511-02: WebKitGTK+: Multiple Vulnerabilities',
            '202511-01: UDisks: Multiple Vulnerabilities', '202509-08: GnuTLS: Multiple Vulnerabilities',
            '202509-07: libvpx: Use after free', '202509-06: ProFTPd: SSH Terrapin vulnerability',
            '202509-05: Plex Media Server: Incorrect resource transfer', '202509-04: glibc: Multiple Vulnerabilities',
            '202509-03: Django: Multiple Vulnerabilities', '202509-02: Spidermonkey: Multiple Vulnerabilities',
            '202509-01: Poppler: Multiple Vulnerabilities', '202508-06: Composer: Multiple Vulnerabilities',
            '202508-05: Spreadsheet-ParseExcel: Arbitrary Code Execution',
            '202508-04: Mozilla Network Security Service (NSS): TLS RSA decryption timing attack',
            '202508-03: FontForge: Arbitrary Code Execution', '202508-02: GPL Ghostscript: Multiple Vulnerabilities',
            '202508-01: PAM: Multiple Vulnerabilities', '202507-10: Roundcube: Multiple Vulnerabilities',
            '202507-09: Git: Multiple Vulnerabilities', '202507-08: REXML: Multiple Vulnerabilities',
            '202507-07: Chromium, Google Chrome, Microsoft Edge. Opera: Multiple Vulnerabilities',
            '202507-06: openh264: Heap Overflow', '202507-05: NTP: Multiple Vulnerabilities',
            '202507-04: strongSwan: Buffer Overflow', '202507-03: ClamAV: Multiple Vulnerabilities',
            '202507-02: UDisks, libblockdev: Privilege escalation', '202507-01: sudo: Privilege escalation',
            '202506-13: Konsole: Code execution', '202506-12: sysstat: Arbitrary Code Execution',
            '202506-11: YAML-LibYAML: Shell injection', '202506-10: File-Find-Rule: Shell Injection',
            '202506-09: OpenImageIO: Multiple Vulnerabilities', '202506-08: Node.js: Multiple Vulnerabilities',
            '202506-07: Python, PyPy: Multiple Vulnerabilities', '202506-06: Qt: Multiple Vulnerabilities',
            '202506-05: GTK+ 3: Search path vulnerability',
            '202506-04: X.Org X server, XWayland: Multiple Vulnerabilities',
            '202506-03: LibreOffice: Multiple Vulnerabilities',
            '202506-02: GStreamer, GStreamer Plugins: Multiple Vulnerabilities',
            '202506-01: Emacs: Multiple Vulnerabilities']


def test_glsa_list(original_html_xml):
    from pyerge.glsa import glsa_list
    with mock.patch('urllib.request.urlopen') as urlopen_mock:
        mock_response = urlopen_mock.return_value.__enter__.return_value
        mock_response.read.return_value = original_html_xml.encode('utf-8')

        assert glsa_list(
            elements=2) == '202601-05: Commons-BeanUtils: Arbitary Code Execution\n202601-04: Asterisk: Multiple Vulnerabilities'


def test_glsa_list_zero_elements():
    from pyerge.glsa import glsa_list

    assert glsa_list(elements=0) == ''


def test_glsa_test_system_not_affected(original_html_xml):
    from pyerge.glsa import glsa_test
    with mock.patch('pyerge.glsa.utils') as utils_mock:
        with mock.patch('urllib.request.urlopen') as urlopen_mock:
            mock_response = urlopen_mock.return_value.__enter__.return_value
            mock_response.read.return_value = original_html_xml.encode('utf-8')
            utils_mock.run_cmd.return_value = b'', b'This system is not affected by any of the listed GLSAs\n'
            assert glsa_test(elements=2) == 'System is not affected by any of listed GLSAs'


def test_glsa_test_system_affected(original_html_xml):
    from pyerge.glsa import glsa_test
    date1 = '202507-02'
    date2 = '202511-01'
    dates = bytes(f'{date1}\n{date2}\n', encoding='ascii')

    with mock.patch('pyerge.glsa.utils') as utils_mock:
        with mock.patch('urllib.request.urlopen') as urlopen_mock:
            mock_response = urlopen_mock.return_value.__enter__.return_value
            mock_response.read.return_value = original_html_xml.encode('utf-8')
            utils_mock.run_cmd.return_value = dates, b'This system is affected by the following GLSAs:\n'
            assert glsa_test(elements=2) == f'{date1},{date2}'


def test_glsa_test_zero_elements():
    from pyerge.glsa import glsa_test

    assert glsa_test(elements=0) == ''


@mark.parametrize('regex, result', [(GLSA_TEST_REGEX, all_dates),
                                    (GLSA_LIST_REGEX, all_vuls)])
def test_collect_all_matching_entries(regex, result, original_html_xml):
    from pyerge.glsa import _collect_all_matching_entries

    assert list(_collect_all_matching_entries(original_html_xml, regex)) == result


def test_collect_all_matching_entries_empty(no_title_text_xml):
    from pyerge.glsa import _collect_all_matching_entries

    assert list(_collect_all_matching_entries(no_title_text_xml, GLSA_LIST_REGEX)) == []
