from argparse import Namespace
from unittest.mock import call, patch

from pytest import mark

from pyerge import tmerge


@mark.parametrize('return_code, pretend, world', [(b'0', False, False), (b'0', True, False),
                                                  (b'0', True, True), (b'1', False, False),
                                                  (b'1', False, True), (b'1', True, False),
                                                  (b'1', True, True)])
def test_deep_clean_not_run(return_code, pretend, world):
    with patch('pyerge.tmerge.check_emerge_opts') as check_emerge_opts_mock, \
            patch('pyerge.tmerge.emerge') as emerge_mock, \
            patch('pyerge.tmerge.deep_run') as deep_run_mock:
        check_emerge_opts_mock.return_value = (pretend, world)
        tmerge.deep_clean([''], Namespace(), return_code)
        emerge_mock.assert_not_called()
        deep_run_mock.assert_not_called()


def test_deep_clean_run():
    with patch('pyerge.tmerge.check_emerge_opts') as check_emerge_opts_mock, \
            patch('pyerge.tmerge.emerge') as emerge_mock, \
            patch('pyerge.tmerge.deep_run') as deep_run_mock:
        opts = Namespace()
        output_and_rc = b'0'
        check_emerge_opts_mock.return_value = (False, True)
        emerge_mock.return_value = (output_and_rc, output_and_rc)
        tmerge.deep_clean([''], opts, output_and_rc)
        emerge_mock.assert_called_once_with(arguments=['-pc'], build=False)
        deep_run_mock.assert_called_once_with(opts, output_and_rc)


def test_deep_run_not_selected():
    with patch('pyerge.tmerge.emerge') as emerge_mock:
        tmerge.deep_run(opts=Namespace(deep_run=False), output=b'')
        emerge_mock.assert_not_called()


def test_deep_run_wrong_output():
    with patch('pyerge.tmerge.emerge') as emerge_mock:
        tmerge.deep_run(opts=Namespace(deep_run=True), output=b'All selected packages: ')
        emerge_mock.assert_not_called()


def test_deep_run_output_with_two_packages():
    with patch('pyerge.tmerge.emerge') as emerge_mock:
        output = b'\n\nAll selected packages: =sys-kernel/gentoo-sources-5.10.76-r1 =dev-python/hypothesis-6.27.1\n\n'
        opts = Namespace(deep_run=True)
        tmerge.deep_run(opts=opts, output=output)
        emerge_mock.assert_called_once_with(arguments=['-c', '=dev-python/hypothesis-6.27.1'], build=True)


def test_deep_run_output_with_only_gentoo():
    with patch('pyerge.tmerge.emerge') as emerge_mock:
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
    assert tmerge.check_emerge_opts(list_str) == result


def test_is_portage_running():
    with patch('pyerge.tmerge.utils') as utils_mock:
        utils_mock.run_cmd.return_value = (b'3456\n', b'')
        assert tmerge.is_portage_running() is True
        utils_mock.run_cmd.assert_called_once_with(cmd='pgrep -f /usr/bin/emerge', use_system=False)


def test_is_portage_not_running():
    with patch('pyerge.tmerge.utils') as utils_mock:
        utils_mock.run_cmd.return_value = (b'', b'')
        assert tmerge.is_portage_running() is False
        utils_mock.run_cmd.assert_called_once_with(cmd='pgrep -f /usr/bin/emerge', use_system=False)


def test_run_emerge_world():
    with patch('pyerge.tmerge.emerge') as emerge_mock, \
            patch('pyerge.tmerge.post_emerge') as post_emerge_mock, \
            patch('pyerge.tmerge.deep_clean') as deep_clean:
        ret_code = b'0'
        emerge_mock.return_value = (ret_code, b'')
        emerge_opts = ['-NDu', '@world']
        opts = Namespace(action='emerge', online=True, deep_print=True, world=True)
        result = tmerge.run_emerge(emerge_opts=emerge_opts, opts=opts)
        assert result == (ret_code, b'')
        post_emerge_mock.assert_called_once_with(emerge_opts, ret_code)
        deep_clean.assert_called_once_with(emerge_opts, opts, ret_code)


def test_run_emerge():
    with patch('pyerge.tmerge.emerge') as emerge_mock:
        ret_code = b'0'
        emerge_mock.return_value = (ret_code, b'')
        emerge_opts = ['-pv', 'app-portage/pyerge']
        opts = Namespace(action='emerge', online=True, deep_print=False, world=False, pretend_world=False, deep_run=False)
        result = tmerge.run_emerge(emerge_opts=emerge_opts, opts=opts)
        assert result == (ret_code, b'')


def test_run_emerge_not_online():
    emerge_opts = ['-qv', 'app-portage/pyerge']
    opts = Namespace(action='emerge', online=False)
    assert tmerge.run_emerge(emerge_opts=emerge_opts, opts=opts) == (b'', b'')


def test_run_check():
    with patch('pyerge.tmerge.check_upd') as check_upd_mock:
        opts = Namespace(action='check', local=True, online=True)
        tmerge.run_check(opts)
        check_upd_mock.assert_called_once_with(opts.local)


@mark.parametrize('action, cmd', [('check', 'smart-live-rebuild --no-color --pretend'),
                                  ('emerge', 'smart-live-rebuild --no-color')])
def test_run_live_check(action, cmd):
    with patch('pyerge.tmerge.utils') as utils_mock:
        utils_mock.run_cmd.return_value = (b'games-engines/openmw:0\ngames-strategy/freeorion:0',
                                           b'*** Found 2 packages to rebuild (out of 4 live packages).')
        opts = Namespace(action=action, live=True, online=True)
        tmerge.run_live(opts)
        utils_mock.run_cmd.assert_called_once_with(cmd, use_system=True)


@mark.parametrize('action', [('check', 'emerge')])
def test_run_live_check_not_online_and_not_live(action):
    opts = Namespace(action=action, live=False, online=False)
    assert tmerge.run_live(opts=opts) == (b'', b'')


@mark.parametrize('build, args, results', [(True, ['--pretend', '--update', '@world'], ( b'0', b'')),
                                           (False, ['--newuse', '--deep', '@world'], (b'\nThese are the packages', b''))])
def test_emerge(build, args, results):
    with patch('pyerge.tmerge.utils') as utils_mock:
        utils_mock.run_cmd.return_value = results
        cmd = f"sudo /usr/bin/emerge --nospinner {' '.join(args)}"
        results = tmerge.emerge(arguments=args, build=build)
        utils_mock.assert_has_calls([call.run_cmd(cmd=cmd, use_system=build)])
        assert results == results
