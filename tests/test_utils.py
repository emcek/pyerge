from unittest.mock import patch, call

from pytest import mark

from pyerge import utils

PORT_TMP_DIR = '/var/tmp/portage'


@mark.parametrize('size, result', [('12K', 12), ('34567k', 34567), ('31M', 31744), ('233m', 238592),
                                   ('2G', 2097152), ('1g', 1048576), ('500', 500), ('450.1', 450)])
def test_convert2blocks(size, result):
    assert utils.convert2blocks(size) == result


@patch('pyerge.utils.run_cmd')
def test_tmpfs_not_mounted(run_cmd_mock):
    run_cmd_mock.return_value = b'/dev/sda2 on /boot type ext2 (rw,noatime,errors=continue,user_xattr,acl)\n' \
                                b'rpc_pipefs on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)\n' \
                                b'none on /run/user/1000 type tmpfs (rw,relatime,mode=700,uid=1000)\n', b''
    assert utils.is_tmpfs_mounted(PORT_TMP_DIR) is False


@patch('pyerge.utils.run_cmd')
def test_tmpfs_mounted(run_cmd_mock):
    run_cmd_mock.return_value = b'/dev/sda2 on /boot type ext2 (rw,noatime,errors=continue,user_xattr,acl)\n' \
                                b'rpc_pipefs on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)\n' \
                                b'none on /run/user/1000 type tmpfs (rw,relatime,mode=700,uid=1000)\n' \
                                b'tmpfs on /var/tmp/portage type tmpfs (rw,relatime,size=1000k,nr_inodes=1048576)\n', b''
    assert utils.is_tmpfs_mounted(PORT_TMP_DIR) is True


@patch('pyerge.utils.run_cmd')
def test_unmounttmpfs(run_cmd_mock):
    utils.unmounttmpfs('2G', True, PORT_TMP_DIR)
    run_cmd_mock.assert_called_once_with(f'sudo umount -f {PORT_TMP_DIR}')


@patch('pyerge.utils.run_cmd')
def test_mounttmpfs(run_cmd_mock):
    utils.mounttmpfs('2G', True, PORT_TMP_DIR)
    run_cmd_mock.assert_called_once_with(f'sudo mount -t tmpfs -o size=2G,nr_inodes=1M tmpfs {PORT_TMP_DIR}')


@patch('pyerge.utils.run_cmd')
def test_remounttmpfs(run_cmd_mock):
    utils.remounttmpfs('2G', True, PORT_TMP_DIR)
    run_cmd_mock.assert_has_calls([call.run_cmd(f'sudo umount -f {PORT_TMP_DIR}'),
                                   call.run_cmd(f'sudo mount -t tmpfs -o size=2G,nr_inodes=1M tmpfs {PORT_TMP_DIR}')])


@patch('pyerge.utils.run_cmd')
def test_size_of_not_mounted_tmpfs(run_cmd_mock):
    run_cmd_mock.return_value = b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n' \
                                b'/dev/sda2          126931    76647      43731  64% /boot\n' \
                                b'none              4043868        0    4043868   0% /run/user/1000\n' \
                                b'tmpfs                1000        0       1000   0% /var/tmp/portage\n', b''
    assert utils.size_of_mounted_tmpfs(PORT_TMP_DIR) == 1000


@patch('pyerge.utils.run_cmd')
def test_size_of_mounted_tmpfs(run_cmd_mock):
    run_cmd_mock.return_value = b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n' \
                                b'/dev/sda2          126931    76647      43731  64% /boot\n' \
                                b'none              4043868        0    4043868   0% /run/user/1000\n', b''
    assert utils.size_of_mounted_tmpfs(PORT_TMP_DIR) == 0


@patch('pyerge.utils.run_cmd')
def test_is_internet_connected(run_cmd_mock):
    run_cmd_mock.return_value = b'PING 89.16.167.134 (89.16.167.134) 56(84) bytes of data.\n' \
                                b'64 bytes from 89.16.167.134: icmp_seq=1 ttl=47 time=52.2 ms\n\n' \
                                b'--- 89.16.167.134 ping statistics ---\n' \
                                b'1 packets transmitted, 1 received, 0% packet loss, time 0ms\n' \
                                b'rtt min/avg/max/mdev = 52.212/52.212/52.212/0.000 ms\n', b''
    assert utils.is_internet_connected() is True


@patch('pyerge.utils.run_cmd')
def test_is_internet_not_connected(run_cmd_mock):
    run_cmd_mock.return_value = b'', b''
    assert utils.is_internet_connected() is False


@patch('pyerge.utils.open')
def test_delete_content(open_mock):
    utils.delete_content('/tmp/emerge.log')
    open_mock.assert_called_once_with('/tmp/emerge.log', 'w')


# @patch('pyerge.utils.Popen')
# def test_run_cmd(popen_mock):
#     popen_mock.communicate.return_value = b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n' \
#                                           b'/dev/sda2          126931    76647      43731  64% /boot\n', \
#                                           b''
#     assert utils.run_cmd('df') == b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n' \
#                                   b'/dev/sda2          126931    76647      43731  64% /boot\n', \
#                                   b''
#     popen_mock.assert_called_once_with()
