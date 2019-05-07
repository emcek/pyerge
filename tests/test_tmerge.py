from unittest import mock

from pytest import mark

from pyerge import tmerge


@mock.patch('pyerge.tmerge.utils')
def test_is_portage_running(utils_mock):
    utils_mock.run_cmd.return_value = (b'3456\n', b'')
    assert tmerge.is_portage_running() is True
    utils_mock.run_cmd.assert_called_once_with('pgrep -f /usr/bin/emerge')


@mock.patch('pyerge.tmerge.utils')
def test_is_portage_not_running(utils_mock):
    utils_mock.run_cmd.return_value = (b'', b'')
    assert tmerge.is_portage_running() is False
    utils_mock.run_cmd.assert_called_once_with('pgrep -f /usr/bin/emerge')


@mark.parametrize('list_str, result', [(['-pvNDu', '@world'], (True, True)),
                                       (['-pv', 'conky'], (True, False)),
                                       (['-f', 'conky'], (False, False)),
                                       (['', '@world'], (False, True)),
                                       (['', 'conky'], (False, False))])
def test_check_emerge_opts(list_str, result):
    assert tmerge.check_emerge_opts(list_str) == result


def test_set_portage_tmpdir(monkeypatch):
    from os import environ
    monkeypatch.setitem(environ, 'PORTAGE_TMPDIR', '')
    assert tmerge.set_portage_tmpdir() == '/var/tmp/portage'


def test_portage_tmpdir_already_set(monkeypatch):
    from os import environ
    monkeypatch.setitem(environ, 'PORTAGE_TMPDIR', 'some_value')
    assert tmerge.set_portage_tmpdir() == 'some_value'
