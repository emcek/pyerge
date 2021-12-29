from unittest.mock import patch

from pytest import mark


@mark.parametrize('return_code, pretend, world', [(b'0', False, False), (b'0', True, False),
                                                  (b'0', True, True), (b'1', False, False),
                                                  (b'1', False, True), (b'1', True, False),
                                                  (b'1', True, True)])
def test_deep_clean_not_run(return_code, pretend, world):
    from argparse import Namespace
    with patch('pyerge.tmerge.check_emerge_opts') as check_emerge_opts_mock, \
            patch('pyerge.tmerge.emerge') as emerge_mock, \
            patch('pyerge.tmerge.deep_run') as deep_run_mock:
        from pyerge import tmerge
        check_emerge_opts_mock.return_value = (pretend, world)
        tmerge.deep_clean([''], Namespace(), return_code)
        emerge_mock.assert_not_called()
        deep_run_mock.assert_not_called()


def test_deep_clean_run():
    from argparse import Namespace
    with patch('pyerge.tmerge.check_emerge_opts') as check_emerge_opts_mock, \
            patch('pyerge.tmerge.emerge') as emerge_mock, \
            patch('pyerge.tmerge.deep_run') as deep_run_mock:
        from pyerge import tmerge
        opts = Namespace()
        output_and_rc = b'0'
        check_emerge_opts_mock.return_value = (False, True)
        emerge_mock.return_value = (output_and_rc, output_and_rc)
        tmerge.deep_clean([''], opts, output_and_rc)
        emerge_mock.assert_called_once_with(['-pc'], build=False)
        deep_run_mock.assert_called_once_with(opts, output_and_rc)


def test_deep_run_not_selected():
    from argparse import Namespace
    with patch('pyerge.tmerge.emerge') as emerge_mock:
        from pyerge import tmerge
        tmerge.deep_run(opts=Namespace(deep_run=False), output=b'')
        emerge_mock.assert_not_called()


def test_deep_run_wrong_output():
    from argparse import Namespace
    with patch('pyerge.tmerge.emerge') as emerge_mock:
        from pyerge import tmerge
        tmerge.deep_run(opts=Namespace(deep_run=True), output=b'All selected packages: ')
        emerge_mock.assert_not_called()


def test_deep_run_output_with_two_packages():
    from argparse import Namespace
    with patch('pyerge.tmerge.emerge') as emerge_mock:
        from pyerge import tmerge
        output = b'\n\nAll selected packages: =sys-kernel/gentoo-sources-5.10.76-r1 =dev-python/hypothesis-6.27.1\n\n'
        opts = Namespace(deep_run=True)
        tmerge.deep_run(opts=opts, output=output)
        emerge_mock.assert_called_once_with(['-c', '=dev-python/hypothesis-6.27.1'], build=True)


def test_deep_run_output_with_only_gentoo():
    from argparse import Namespace
    with patch('pyerge.tmerge.emerge') as emerge_mock:
        from pyerge import tmerge
        output = b'\n\nAll selected packages: =sys-kernel/gentoo-sources-5.10.76-r1\n\n'
        opts = Namespace(deep_run=True)
        tmerge.deep_run(opts=opts, output=output)
        emerge_mock.assert_not_called()


@mark.parametrize('list_str, result', [(['--pretend', '--verbose', '--newuse', '--deep', '--update', '@world'], (True, True)),
                                       (['--pretend', '--verbose', 'conky'], (True, False)),
                                       (['-f', 'conky'], (False, False)),
                                       (['', '@world'], (False, True)),
                                       (['', 'conky'], (False, False))])
def test_check_emerge_opts(list_str, result):
    from pyerge import tmerge
    assert tmerge.check_emerge_opts(list_str) == result


def test_is_portage_running():
    from pyerge import tmerge
    with patch('pyerge.tmerge.utils') as utils_mock:
        utils_mock.run_cmd.return_value = (b'3456\n', b'')
        assert tmerge.is_portage_running() is True
        utils_mock.run_cmd.assert_called_once_with('pgrep -f /usr/bin/emerge')


def test_is_portage_not_running():
    from pyerge import tmerge
    with patch('pyerge.tmerge.utils') as utils_mock:
        utils_mock.run_cmd.return_value = (b'', b'')
        assert tmerge.is_portage_running() is False
        utils_mock.run_cmd.assert_called_once_with('pgrep -f /usr/bin/emerge')


def test_run_emerge():
    from argparse import Namespace
    with patch('pyerge.tmerge.emerge') as emerge_mock, \
            patch('pyerge.tmerge.post_emerge') as post_emerge_mock, \
            patch('pyerge.tmerge.deep_clean') as deep_clean:
        ret_code = b'0'
        emerge_mock.return_value = (ret_code, b'')
        from pyerge import tmerge
        emerge_opts = ['-NDu', '@world']
        opts = Namespace(action='emerge', online=True, deep_print=True)
        tmerge.run_emerge(emerge_opts=emerge_opts, opts=opts)
        post_emerge_mock.assert_called_once_with(emerge_opts, ret_code)
        deep_clean.assert_called_once_with(emerge_opts, opts, ret_code)


def test_run_check():
    from argparse import Namespace
    with patch('pyerge.tmerge.check_upd') as check_upd_mock:
        from pyerge import tmerge
        opts = Namespace(action='check', local=True, online=True)
        tmerge.run_check(opts)
        check_upd_mock.assert_called_once_with(opts.local)
