from unittest.mock import patch

from pytest import raises
from pyerge import utils, tmerge


def test_cli_system_exit():
    with raises(SystemExit) as sys_mock:
        from pyerge import cli
        cli.run_parser()
    assert sys_mock.value.code > 0


def test_main_exec_portage_is_running():
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


# def test_main_exec_2():
#     from argparse import Namespace
#     with patch('pyerge.cli.utils') as utils_is_internet_connected_mock, patch('pyerge.cli.tmerge') as tmerge_is_portage_running_mock:
#         utils_is_internet_connected_mock.return_value.is_internet_connected.return_value = True
#         tmerge_is_portage_running_mock.return_value.is_portage_running.return_value = True
#         from pyerge import cli
#         opts = Namespace(world=False, pretend_world=False, pretend=False, quiet=False, verbose=True)
#         emerge_opts = ['']
#         cli.main_exec(opts, emerge_opts)
#         utils_is_internet_connected_mock.assert_called_once_with(opts.verbose)
#         tmerge_is_portage_running_mock.assert_called_once()


def test_main_exec_portage_is_not_running():
    from argparse import Namespace
    with patch.object(utils, 'is_internet_connected') as is_internet_connected_mock, \
            patch.object(utils, 'set_portage_tmpdir') as set_portage_tmpdir_mock, \
            patch.object(utils, 'handling_mounting') as handling_mounting_mock, \
            patch.object(utils, 'unmounttmpfs') as unmounttmpfs_mock, \
            patch.object(tmerge, 'is_portage_running') as is_portage_running_mock, \
            patch.object(tmerge, 'run_emerge') as run_emerge_mock, \
            patch.object(tmerge, 'run_check') as run_check_mock:
        is_internet_connected_mock.return_value = True
        is_portage_running_mock.return_value = False
        from pyerge import cli
        opts = Namespace(world=False, pretend_world=False, pretend=False, quiet=False, verbose=True)
        emerge_opts = ['']
        cli.main_exec(opts, emerge_opts)
        is_internet_connected_mock.assert_called_once_with(opts.verbose)
        set_portage_tmpdir_mock.assert_called_once()
        handling_mounting_mock.assert_called_once_with(opts)
        unmounttmpfs_mock.assert_called_once_with(opts)
        is_portage_running_mock.assert_called_once()
        run_emerge_mock.assert_called_once_with(emerge_opts, opts)
        run_check_mock.assert_called_once_with(opts)
