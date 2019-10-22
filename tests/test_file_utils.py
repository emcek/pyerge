from sys import version_info
from unittest import mock
from unittest.mock import mock_open, Mock

from pytest import mark

from pyerge.file_utils import e_sync, e_dl, e_curr, e_eut


def test_synced(str_sync):
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_sync.split('\n'))))
        assert e_sync() == 'Tuesday 22:01' or 'Tuesday 23:01'


def test_no_synced(str_no_sync):
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_no_sync.split('\n'))))
        assert e_sync() == 'Unknown'


@mark.skipif(condition=version_info < (3, 7), reason='Run only on Python 3.7+')
def test_synced_ver2(str_sync):
    with mock.patch('pyerge.file_utils.open', mock_open(read_data=str_sync)) as m:
        result = e_sync()

    m.assert_called_once_with('/var/log/emerge.log')
    assert result == 'Tuesday 22:01' or 'Tuesday 23:01'


def test_e_dl_gt_zero(str_dl_gt_0):
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_dl_gt_0.split('\n'))))
        assert e_dl() == '283,699 KiB'


def test_e_dl_eq_zero(str_dl_eq_0):
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_dl_eq_0.split('\n'))))
        assert e_dl() == 'None'


def test_e_dl_unknown(str_dl_unknown):
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_dl_unknown.split('\n'))))
        assert e_dl() == 'Calculating...'


def test_e_curr(str_curr):
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_curr.split('\n'))))
        assert e_curr() == 'sys-kernel/linux-firmware-20191008'


def test_e_curr_empty(str_curr_empty):
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_curr_empty.split('\n'))))
        assert e_curr() == ''


def test_e_eut(str_eut):
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_eut.split('\n'))))
        assert e_eut() == '1h 9min'


def test_e_eut_unknown(str_eut_unknown):
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_eut_unknown.split('\n'))))
        assert e_eut() == 'Unknown'
