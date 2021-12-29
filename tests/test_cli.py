from unittest.mock import patch

from pytest import raises, mark


def test_cli_system_exit():
    with raises(SystemExit) as sys_mock:
        from pyerge import cli
        cli.run_parser()
    assert sys_mock.value.code > 0


def test_run_parser_with_correct_action():
    from argparse import Namespace, ArgumentParser
    with patch.object(ArgumentParser, 'parse_known_args') as argument_parser_mock, patch('pyerge.cli.main_exec') as main_exec_mock:
        opts = Namespace(action='emerge', world=True, verbose=1, quiet=True)
        emerge_opts = ['-NDu', '@world']
        argument_parser_mock.return_value = (opts, emerge_opts)
        from pyerge import cli
        cli.run_parser()
        main_exec_mock.assert_called_once_with(opts, emerge_opts)


def test_main_exec_portage_is_running():
    from pyerge import utils, tmerge
    from argparse import Namespace
    with patch.object(utils, 'is_internet_connected') as is_internet_connected_mock, patch.object(tmerge, 'is_portage_running') as is_portage_running_mock:
        is_internet_connected_mock.return_value = True
        is_portage_running_mock.return_value = True
        from pyerge import cli
        opts = Namespace(world=False, pretend_world=False, pretend=False, quiet=False, verbose=0)
        emerge_opts = ['']
        cli.main_exec(opts, emerge_opts)
        is_internet_connected_mock.assert_called_once_with()
        is_portage_running_mock.assert_called_once()


@mark.parametrize('ns_args, emerge_opts, result',
                  [({'world': True, 'pretend_world': False, 'quiet': False, 'verbose': 2},
                    [''],
                    ['--with-bdeps=y', '--keep-going=y', '--newuse', '--deep', '--update', '@world']),
                   ({'world': True, 'pretend_world': False, 'quiet': True, 'verbose': 2},
                    [''],
                    ['--with-bdeps=y', '--keep-going=y', '--newuse', '--deep', '--update', '@world']),
                   ({'world': False, 'pretend_world': True, 'quiet': False, 'verbose': 2},
                    [''],
                    ['--with-bdeps=y', '--pretend', '--verbose', '--newuse', '--deep', '--update', '@world']),
                   ({'world': False, 'pretend_world': True, 'quiet': True, 'verbose': 2},
                    [''],
                    ['--with-bdeps=y', '--pretend', '--verbose', '--newuse', '--deep', '--update', '@world']),
                   ({'world': False, 'pretend_world': False, 'quiet': False, 'verbose': 2},
                    ['-av', 'app-misc/mc'],
                    ['-av', 'app-misc/mc']),
                   ({'world': False, 'pretend_world': False, 'quiet': True, 'verbose': 2},
                    ['-av', 'app-misc/mc'],
                    ['-av', 'app-misc/mc'])])
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
        is_internet_connected_mock.assert_called_once_with()
        set_portage_tmpdir_mock.assert_called_once()
        handling_mounting_mock.assert_called_once_with(opts)
        unmounttmpfs_mock.assert_called_once_with(opts)
        is_portage_running_mock.assert_called_once()
        run_emerge_mock.assert_called_once_with(result, opts)
        run_check_mock.assert_called_once_with(opts)
