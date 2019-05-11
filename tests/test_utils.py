from unittest import mock

from pytest import mark

from pyerge import utils

PORT_TMP_DIR = '/var/tmp/portage'


@mark.parametrize('size, result', [('12K', 12), ('34567k', 34567), ('31M', 31744), ('233m', 238592),
                                   ('2G', 2097152), ('1g', 1048576), ('500', 500), ('450.1', 450)])
def test_convert2blocks(size, result):
    assert utils.convert2blocks(size) == result


def test_tmpfs_not_mounted():
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'/dev/sda2 on /boot type ext2 (rw,noatime,errors=continue,user_xattr,acl)\n' \
                                    b'rpc_pipefs on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)\n' \
                                    b'none on /run/user/1000 type tmpfs (rw,relatime,mode=700,uid=1000)\n', b''
        assert utils.is_tmpfs_mounted() is False


def test_tmpfs_mounted():
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'/dev/sda2 on /boot type ext2 (rw,noatime,errors=continue,user_xattr,acl)\n' \
                                    b'rpc_pipefs on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)\n' \
                                    b'none on /run/user/1000 type tmpfs (rw,relatime,mode=700,uid=1000)\n' \
                                    b'tmpfs on /var/tmp/portage type tmpfs (rw,relatime,size=1000k,nr_inodes=1048576)\n', b''
        assert utils.is_tmpfs_mounted() is True


def test_unmounttmpfs():
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        utils.unmounttmpfs('2G', True)
        run_cmd_mock.assert_called_once_with(f'sudo umount -f {PORT_TMP_DIR}')


def test_mounttmpfs():
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        utils.mounttmpfs('2G', True)
        run_cmd_mock.assert_called_once_with(f'sudo mount -t tmpfs -o size=2G,nr_inodes=1M tmpfs {PORT_TMP_DIR}')


def test_remounttmpfs():
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        utils.remounttmpfs('2G', True)
        run_cmd_mock.assert_has_calls([mock.call.run_cmd(f'sudo umount -f {PORT_TMP_DIR}'),
                                       mock.call.run_cmd(f'sudo mount -t tmpfs -o size=2G,nr_inodes=1M tmpfs {PORT_TMP_DIR}')])


def test_size_of_not_mounted_tmpfs():
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n' \
                                    b'/dev/sda2          126931    76647      43731  64% /boot\n' \
                                    b'none              4043868        0    4043868   0% /run/user/1000\n' \
                                    b'tmpfs                1000        0       1000   0% /var/tmp/portage\n', b''
        assert utils.size_of_mounted_tmpfs() == 1000


def test_size_of_mounted_tmpfs():
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n' \
                                    b'/dev/sda2          126931    76647      43731  64% /boot\n' \
                                    b'none              4043868        0    4043868   0% /run/user/1000\n', b''
        assert utils.size_of_mounted_tmpfs() == 0


def test_is_internet_connected():
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'PING 89.16.167.134 (89.16.167.134) 56(84) bytes of data.\n' \
                                    b'64 bytes from 89.16.167.134: icmp_seq=1 ttl=47 time=52.2 ms\n\n' \
                                    b'--- 89.16.167.134 ping statistics ---\n' \
                                    b'1 packets transmitted, 1 received, 0% packet loss, time 0ms\n' \
                                    b'rtt min/avg/max/mdev = 52.212/52.212/52.212/0.000 ms\n', b''
        assert utils.is_internet_connected(verbose=True) is True


def test_is_internet_not_connected():
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'', b''
        assert utils.is_internet_connected(verbose=True) is False


def test_delete_content():
    with mock.patch('pyerge.utils.open') as open_mock:
        utils.delete_content('/tmp/emerge.log')
        open_mock.assert_called_once_with('/tmp/emerge.log', 'w')


def test_run_cmd_as_subprocess():
    with mock.patch('pyerge.utils.Popen') as popen_mock:
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': (b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n'
                                              b'/dev/sda2          126931    76647      43731  64% /boot\n', b'')}
        process_mock.configure_mock(**attrs)
        popen_mock.return_value = process_mock
        assert utils.run_cmd('df') == (b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n'
                                       b'/dev/sda2          126931    76647      43731  64% /boot\n', b'')
        popen_mock.assert_called_once_with(['df'], stderr=-1, stdout=-1)


def test_run_cmd_as_sysyem():
    with mock.patch('pyerge.utils.system') as system_mock:
        system_mock.return_value = 0
        assert utils.run_cmd('df', use_system=True) == (b'0', b'')
        system_mock.assert_called_once_with('df')


def test_set_portage_tmpdir(monkeypatch):
    from os import environ
    monkeypatch.setitem(environ, 'PORTAGE_TMPDIR', '')
    assert utils.set_portage_tmpdir() == '/var/tmp/portage'


def test_portage_tmpdir_already_set(monkeypatch):
    from os import environ
    monkeypatch.setitem(environ, 'PORTAGE_TMPDIR', 'some_value')
    assert utils.set_portage_tmpdir() == 'some_value'
