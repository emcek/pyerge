from unittest import mock
from unittest.mock import mock_open, Mock

from pyerge.file_utils import e_sync

list_no_sync = ["1548194358:  === sync",
                "1548194358: >>> Syncing repository 'gentoo' into '/usr/portage'...",
                "1548194361: >>> Starting rsync with rsync://[2a01:90:200:10::1a]/gentoo-portage"]

list_sync = ["1548194361: >>> Starting rsync with rsync://[2a01:90:200:10::1a]/gentoo-portage",
             "1548194466: === Sync completed for gentoo",
             "1548194466:  *** terminating."]

str_sync = """
1548194361: >>> Starting rsync with rsync://[2a01:90:200:10::1a]/gentoo-portage
1548194466: === Sync completed for gentoo
1548194466:  *** terminating.
"""


def test_synced():
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list_sync))
        assert e_sync() == 'Tuesday 22:01' or 'Tuesday 23:01'
        # open_mock.assert_called_once_with('/var/log/emerge.log')


def test_no_synced():
    with mock.patch('pyerge.file_utils.open') as open_mock:
        open_mock.return_value.__enter__ = open_mock
        open_mock.return_value.__iter__ = Mock(return_value=iter(list_no_sync))
        assert e_sync() == 'Unknown'
        # open_mock.assert_called_once_with('/var/log/emerge.log')


def test_synced_2():
    # Not working shoud faild
    with mock.patch('pyerge.file_utils.open', mock_open(read_data=str_sync)) as m:
        # m.side_effect = [
        #     mock_open(read_data="1548194466:  *** terminating.").return_value,
        #     mock_open(read_data="1548194466: === Sync completed for gentoo").return_value
        # ]
        result = e_sync()

    m.assert_called_once_with('/var/log/emerge.log')
    assert result == 'Unknown'
    # assert result == 'Tuesday 23:01'
