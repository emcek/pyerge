from unittest import mock

from pytest import mark

from pyerge import tmerge


def test_is_portage_running():
    with mock.patch('pyerge.tmerge.utils') as utils_mock:
        utils_mock.run_cmd.return_value = (b'3456\n', b'')
        assert tmerge.is_portage_running() is True
        utils_mock.run_cmd.assert_called_once_with('pgrep -f /usr/bin/emerge')


def test_is_portage_not_running():
    with mock.patch('pyerge.tmerge.utils') as utils_mock:
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
