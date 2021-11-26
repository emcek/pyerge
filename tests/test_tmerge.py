from unittest.mock import patch

from pytest import mark


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
        opts = Namespace(deep_run=True, verbose=2)
        tmerge.deep_run(opts=opts, output=output)
        emerge_mock.assert_called_once_with(['-c', '=dev-python/hypothesis-6.27.1'], opts.verbose, build=True)


def test_deep_run_output_with_only_gentoo():
    from argparse import Namespace
    with patch('pyerge.tmerge.emerge') as emerge_mock:
        from pyerge import tmerge
        output = b'\n\nAll selected packages: =sys-kernel/gentoo-sources-5.10.76-r1\n\n'
        opts = Namespace(deep_run=True)
        tmerge.deep_run(opts=opts, output=output)
        emerge_mock.assert_not_called()


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
    with patch('pyerge.tmerge.emerge') as emerge_mock, patch('pyerge.tmerge.post_emerge') as postemerge_mock, patch('pyerge.tmerge.deep_clean') as clean_mock:
        ret_code = b'0'
        emerge_mock.return_value = (ret_code, b'')
        from pyerge import tmerge
        emerge_opts = ['-NDu', '@world']
        opts = Namespace(action='emerge', online=True, verbose=2, deep_print=True)
        tmerge.run_emerge(emerge_opts=emerge_opts, opts=opts)
        postemerge_mock.assert_called_once_with(emerge_opts, opts.verbose, ret_code)
        clean_mock.assert_called_once_with(emerge_opts, opts, ret_code)


def test_run_check():
    from argparse import Namespace
    with patch('pyerge.tmerge.check_upd') as check_upd_mock:
        from pyerge import tmerge
        opts = Namespace(action='check', local=True, verbose=2, online=True)
        tmerge.run_check(opts)
        check_upd_mock.assert_called_once_with(opts.local, opts.verbose)
