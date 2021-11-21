from sys import version_info
from unittest import mock
from unittest.mock import mock_open, Mock

from pytest import mark

from pyerge import tools


def test_synced(str_sync):
    with mock.patch('pyerge.tools.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_sync.split('\n'))))
        assert tools.e_sync() == 'Tuesday 22:01' or 'Tuesday 23:01'


def test_no_synced(str_no_sync):
    with mock.patch('pyerge.tools.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_no_sync.split('\n'))))
        assert tools.e_sync() == 'Unknown'


@mark.skipif(condition=version_info < (3, 7), reason='Run only on Python 3.7+')
def test_synced_ver2(str_sync):
    with mock.patch('pyerge.tools.open', mock_open(read_data=str_sync)) as m:
        result = tools.e_sync()

    m.assert_called_once_with(file='/var/log/emerge.log', encoding='utf-8')
    assert result == 'Tuesday 22:01' or 'Tuesday 23:01'


def test_e_dl_gt_zero(str_dl_gt_0):
    with mock.patch('pyerge.tools.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_dl_gt_0.split('\n'))))
        assert tools.e_dl() == '283,699 KiB'


def test_e_dl_eq_zero(str_dl_eq_0):
    with mock.patch('pyerge.tools.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_dl_eq_0.split('\n'))))
        assert tools.e_dl() == 'None'


def test_e_dl_unknown(str_dl_unknown):
    with mock.patch('pyerge.tools.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_dl_unknown.split('\n'))))
        assert tools.e_dl() == 'Calculating...'


def test_e_curr(str_curr):
    with mock.patch('pyerge.tools.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_curr.split('\n'))))
        assert tools.e_curr() == 'sys-kernel/linux-firmware-20191008'


def test_e_curr_empty(str_curr_empty):
    with mock.patch('pyerge.tools.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_curr_empty.split('\n'))))
        assert tools.e_curr() == ''


def test_e_eut(str_eut):
    with mock.patch('pyerge.tools.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_eut.split('\n'))))
        assert tools.e_eut() == '1h 9min'


def test_e_eut_unknown(str_eut_unknown):
    with mock.patch('pyerge.tools.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_eut_unknown.split('\n'))))
        assert tools.e_eut() == 'Unknown'


def test_e_eta_no_working_merge():
    with mock.patch('pyerge.tools.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'!!! Error: no working merge found.\n' \
                                    b'(the -c option only works if there is an ongoing compilation, see manpage)\n', b''
        assert tools.e_eta() == 'Unknown'


def test_e_eta_emerge_working():
    with mock.patch('pyerge.tools.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'\n Currently merging 1 out of 1\n\n' \
                                    b' * app-text/openjade-1.3.2-r9\n\n' \
                                    b'       current merge time: 9 seconds.\n' \
                                    b'       ETA: 1 minute and 21 seconds.\n', b''
        assert tools.e_eta() == '1 minute and 21 seconds'


def test_e_raid_match():
    with mock.patch('pyerge.tools.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'Personalities : [linear] [raid0] [raid1] [raid10] [raid6] [raid5] [raid4] \n' \
                                    b'md16 : active raid5 sdc1[4] sdb1[1] sdd1[3]\n' \
                                    b'      1935409152 blocks super 1.2 level 5, 512k chunk, algorithm 2 [3/3] [_UU]\n' \
                                    b'      bitmap: 1/8 pages [4KB], 65536KB chunk\n\n' \
                                    b'md17 : active raid5 sdc2[4] sdb2[1] sdd2[3]\n' \
                                    b'      17835008 blocks super 1.2 level 5, 512k chunk, algorithm 2 [3/3] [UU_]\n' \
                                    b'      \nunused devices: <none>\n', b''
        assert tools.e_raid('md16') == '[_UU]'
        assert tools.e_raid('md17') == '[UU_]'


def test_e_raid_not_match():
    with mock.patch('pyerge.tools.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'', b''
        assert tools.e_raid('md16') == 'Unknown'
