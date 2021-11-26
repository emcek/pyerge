from unittest import mock

from pytest import mark


@mark.parametrize('list_str, result', [(['-pvNDu', '@world'], (True, True)),
                                       (['-pv', 'conky'], (True, False)),
                                       (['-f', 'conky'], (False, False)),
                                       (['', '@world'], (False, True)),
                                       (['', 'conky'], (False, False))])
def test_check_emerge_opts(list_str, result):
    from pyerge import tmerge
    assert tmerge.check_emerge_opts(list_str) == result


def test_is_portage_running():
    from pyerge import tmerge
    with mock.patch('pyerge.tmerge.utils') as utils_mock:
        utils_mock.run_cmd.return_value = (b'3456\n', b'')
        assert tmerge.is_portage_running() is True
        utils_mock.run_cmd.assert_called_once_with('pgrep -f /usr/bin/emerge')


def test_is_portage_not_running():
    from pyerge import tmerge
    with mock.patch('pyerge.tmerge.utils') as utils_mock:
        utils_mock.run_cmd.return_value = (b'', b'')
        assert tmerge.is_portage_running() is False
        utils_mock.run_cmd.assert_called_once_with('pgrep -f /usr/bin/emerge')


def test_run_emerge():
    from argparse import Namespace
    with mock.patch('pyerge.tmerge.emerge') as emerge_mock:
        with mock.patch('pyerge.tmerge.post_emerge') as post_emerge_mock:
            with mock.patch('pyerge.tmerge.deep_clean') as deep_clean_mock:
                ret_code = b'0'
                emerge_mock.return_value = (ret_code, b'')
                from pyerge import tmerge
                emerge_opts = ['-NDu', '@world']
                opts = Namespace(action='emerge', online=True, verbose=2, deep_print=True)
                tmerge.run_emerge(emerge_opts=emerge_opts, opts=opts)
                post_emerge_mock.assert_called_once_with(emerge_opts, opts.verbose, ret_code)
                deep_clean_mock.assert_called_once_with(emerge_opts, opts, ret_code)


def test_run_check():
    from argparse import Namespace
    with mock.patch('pyerge.tmerge.check_upd') as check_upd_mock:
        from pyerge import tmerge
        opts = Namespace(action='check', local=True, verbose=2, online=True)
        tmerge.run_check(opts)
        check_upd_mock.assert_called_once_with(opts.local, opts.verbose)
