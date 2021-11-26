from unittest.mock import patch

from pytest import raises, mark


def test_cli_system_exit():
    with raises(SystemExit) as sys_mock:
        from pyerge import cli
        cli.run_parser()
    assert sys_mock.value.code > 0


def test_main_exec_portage_is_running():
    from pyerge import utils, tmerge
    from argparse import Namespace
    with patch.object(utils, 'is_internet_connected') as is_internet_connected_mock, patch.object(tmerge, 'is_portage_running') as is_portage_running_mock:
        is_internet_connected_mock.return_value = True
        is_portage_running_mock.return_value = True
        from pyerge import cli
        opts = Namespace(world=False, pretend_world=False, pretend=False, quiet=False, verbose=True)
        emerge_opts = ['']
        cli.main_exec(opts, emerge_opts)
        is_internet_connected_mock.assert_called_once_with(opts.verbose)
        is_portage_running_mock.assert_called_once()


@mark.parametrize('ns_args, emerge_opts, result',
                  [({'world': True, 'pretend_world': False, 'pretend': False, 'quiet': False, 'verbose': 2}, [''], ['-NDu', '@world']),
                   ({'world': True, 'pretend_world': False, 'pretend': False, 'quiet': True, 'verbose': 2}, [''], ['-NDuq', '@world']),
                   ({'world': False, 'pretend_world': True, 'pretend': False, 'quiet': False, 'verbose': 2}, [''], ['-pvNDu', '@world']),
                   ({'world': False, 'pretend_world': True, 'pretend': False, 'quiet': True, 'verbose': 2}, [''], ['-pvNDuq', '@world']),
                   ({'world': False, 'pretend_world': False, 'pretend': True, 'quiet': False, 'verbose': 2}, ['-av', 'app-misc/mc'], ['-avp', 'app-misc/mc']),
                   ({'world': False, 'pretend_world': False, 'pretend': False, 'quiet': True, 'verbose': 2}, ['-av', 'app-misc/mc'], ['-avq', 'app-misc/mc'])])
def test_emerge_opts_world(ns_args, emerge_opts, result):
    from pyerge import utils, tmerge
    from argparse import Namespace
    with patch.object(utils, 'is_internet_connected') as is_internet_connected_mock, \
            patch.object(utils, 'set_portage_tmpdir') as set_portage_tmpdir_mock, \
            patch.object(utils, 'handling_mounting') as handling_mounting_mock, \
            patch.object(utils, 'unmounttmpfs') as unmounttmpfs_mock, \
            patch.object(tmerge, 'is_portage_running') as is_portage_running_mock, \
            patch.object(tmerge, 'run_emerge') as run_emerge_mock, \
            patch.object(tmerge, 'run_check') as run_check_mock:
        is_internet_connected_mock.return_value = False
        is_portage_running_mock.return_value = False
        from pyerge import cli
        opts = Namespace(**ns_args)
        cli.main_exec(opts, emerge_opts)
        is_internet_connected_mock.assert_called_once_with(opts.verbose)
        set_portage_tmpdir_mock.assert_called_once()
        handling_mounting_mock.assert_called_once_with(opts)
        unmounttmpfs_mock.assert_called_once_with(opts)
        is_portage_running_mock.assert_called_once()
        run_emerge_mock.assert_called_once_with(result, opts)
        run_check_mock.assert_called_once_with(opts)
