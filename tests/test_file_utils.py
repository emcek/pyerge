from sys import version_info
from unittest import mock
from unittest.mock import mock_open, Mock

from pytest import mark

from pyerge.file_utils import e_sync

str_no_sync = """1548194358:  === sync
1548194358: >>> Syncing repository 'gentoo' into '/usr/portage'...
1548194361: >>> Starting rsync with rsync://[2a01:90:200:10::1a]/gentoo-portage"""

str_sync = """1548194361: >>> Starting rsync with rsync://[2a01:90:200:10::1a]/gentoo-portage
1548194466: === Sync completed for gentoo
1548194466:  *** terminating."""


def test_synced():
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_sync.split('\n'))))
        assert e_sync() == 'Tuesday 22:01' or 'Tuesday 23:01'


def test_no_synced():
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list(str_no_sync.split('\n'))))
        assert e_sync() == 'Unknown'


@mark.skipif(condition=version_info < (3, 7), reason='Run only on Python 3.7+')
def test_synced_ver2():
    with mock.patch('pyerge.file_utils.open', mock_open(read_data=str_sync)) as m:
        result = e_sync()

    m.assert_called_once_with('/var/log/emerge.log')
    assert result == 'Tuesday 22:01' or 'Tuesday 23:01'
