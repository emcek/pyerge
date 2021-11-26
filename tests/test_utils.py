from unittest import mock

from pytest import mark


PORT_TMP_DIR = '/var/tmp/portage'


@mark.parametrize('size, result', [('12K', 12), ('34567k', 34567), ('31M', 31744), ('233m', 238592),
                                   ('2G', 2097152), ('1g', 1048576), ('500', 500), ('450.1', 450)])
def test_convert2blocks(size, result):
    from pyerge import utils
    assert utils.convert2blocks(size) == result


def test_tmpfs_not_mounted():
    from pyerge import utils
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'/dev/sda2 on /boot type ext2 (rw,noatime,errors=continue,user_xattr,acl)\n' \
                                    b'rpc_pipefs on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)\n' \
                                    b'none on /run/user/1000 type tmpfs (rw,relatime,mode=700,uid=1000)\n', b''
        assert utils.is_tmpfs_mounted() is False


def test_tmpfs_mounted():
    from pyerge import utils
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'/dev/sda2 on /boot type ext2 (rw,noatime,errors=continue,user_xattr,acl)\n' \
                                    b'rpc_pipefs on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw,relatime)\n' \
                                    b'none on /run/user/1000 type tmpfs (rw,relatime,mode=700,uid=1000)\n' \
                                    b'tmpfs on /var/tmp/portage type tmpfs (rw,relatime,size=1000k,nr_inodes=1048576)\n', b''
        assert utils.is_tmpfs_mounted() is True


def test_unmounttmpfs(opt_emerge_nonlocal_with_1g):
    from pyerge import utils
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        utils.unmounttmpfs(opt_emerge_nonlocal_with_1g)
        run_cmd_mock.assert_called_once_with(f'sudo umount -f {PORT_TMP_DIR}')


def test_mounttmpfs():
    from pyerge import utils
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        utils.mounttmpfs(size='2G')
        run_cmd_mock.assert_called_once_with(f'sudo mount -t tmpfs -o size=2G,nr_inodes=1M tmpfs {PORT_TMP_DIR}')


def test_remounttmpfs():
    from pyerge import utils
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        utils.remounttmpfs(size='2G')
        run_cmd_mock.assert_has_calls([mock.call.run_cmd(f'sudo umount -f {PORT_TMP_DIR}'),
                                       mock.call.run_cmd(f'sudo mount -t tmpfs -o size=2G,nr_inodes=1M tmpfs {PORT_TMP_DIR}')])


def test_size_of_not_mounted_tmpfs():
    from pyerge import utils
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n' \
                                    b'/dev/sda2          126931    76647      43731  64% /boot\n' \
                                    b'none              4043868        0    4043868   0% /run/user/1000\n' \
                                    b'tmpfs                1000        0       1000   0% /var/tmp/portage\n', b''
        assert utils.size_of_mounted_tmpfs() == 1000


def test_size_of_mounted_tmpfs():
    from pyerge import utils
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n' \
                                    b'/dev/sda2          126931    76647      43731  64% /boot\n' \
                                    b'none              4043868        0    4043868   0% /run/user/1000\n', b''
        assert utils.size_of_mounted_tmpfs() == 0


def test_is_internet_connected():
    from pyerge import utils
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'PING 89.16.167.134 (89.16.167.134) 56(84) bytes of data.\n' \
                                    b'64 bytes from 89.16.167.134: icmp_seq=1 ttl=47 time=52.2 ms\n\n' \
                                    b'--- 89.16.167.134 ping statistics ---\n' \
                                    b'1 packets transmitted, 1 received, 0% packet loss, time 0ms\n' \
                                    b'rtt min/avg/max/mdev = 52.212/52.212/52.212/0.000 ms\n', b''
        assert utils.is_internet_connected() is True


def test_is_internet_not_connected():
    from pyerge import utils
    with mock.patch('pyerge.utils.run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = b'', b''
        assert utils.is_internet_connected() is False


def test_delete_content():
    from pyerge import utils
    with mock.patch('pyerge.utils.open') as open_mock:
        utils.delete_content(fname='/tmp/emerge.log')
        open_mock.assert_called_once_with(file='/tmp/emerge.log', mode='w', encoding='utf-8')


def test_run_cmd_as_subprocess_ver1():
    from pyerge import utils
    with mock.patch('pyerge.utils.Popen') as popen_mock:
        process_mock = mock.Mock()
        out = b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n' \
              b'/dev/sda2          126931    76647      43731  64% /boot\n'
        err = b''
        attrs = {'communicate.return_value': (out, err)}
        process_mock.configure_mock(**attrs)
        popen_mock.return_value = process_mock
        assert utils.run_cmd(cmd='df') == (out, err)
        popen_mock.assert_called_once_with(['df'], stderr=-1, stdout=-1)


def test_run_cmd_as_subprocess_ver2():
    from pyerge import utils
    from subprocess import Popen
    with mock.patch.object(Popen, 'communicate') as communicate_mock:
        out = b'Filesystem      1K-blocks     Used  Available Use% Mounted on\n' \
              b'/dev/sda2          126931    76647      43731  64% /boot\n'
        err = b''
        communicate_mock.return_value = (out, err)
        assert utils.run_cmd(cmd='df') == (out, err)
        communicate_mock.assert_called_once_with()


def test_run_cmd_as_sysyem():
    from pyerge import utils
    with mock.patch('pyerge.utils.system') as system_mock:
        system_mock.return_value = 0
        assert utils.run_cmd(cmd='df', use_system=True) == (b'0', b'')
        system_mock.assert_called_once_with('df')


def test_set_portage_tmpdir(monkeypatch):
    from os import environ
    from pyerge import utils
    monkeypatch.setitem(environ, 'PORTAGE_TMPDIR', '')
    assert utils.set_portage_tmpdir() == '/var/tmp/portage'


def test_portage_tmpdir_already_set(monkeypatch):
    from os import environ
    from pyerge import utils
    monkeypatch.setitem(environ, 'PORTAGE_TMPDIR', 'some_value')
    assert utils.set_portage_tmpdir() == 'some_value'


def test_handling_mounting_mount(opt_emerge_nonlocal_with_1g):
    from pyerge import utils
    with mock.patch('pyerge.utils.mounttmpfs') as mounttmpfs_mock:
        with mock.patch('pyerge.utils.is_tmpfs_mounted') as is_tmpfs_mounted_mock:
            is_tmpfs_mounted_mock.return_value = False
            mounttmpfs_mock.return_value = None
            utils.handling_mounting(opt_emerge_nonlocal_with_1g)


def test_handling_mounting_remounte(opt_emerge_nonlocal_with_1g):
    from pyerge import utils
    with mock.patch('pyerge.utils.size_of_mounted_tmpfs') as size_of_mounted_tmpfs_mock:
        with mock.patch('pyerge.utils.convert2blocks') as convert2blocks_mock:
            with mock.patch('pyerge.utils.is_tmpfs_mounted') as is_tmpfs_mounted_mock:
                is_tmpfs_mounted_mock.return_value = True
                size_of_mounted_tmpfs_mock.return_value = 2
                convert2blocks_mock.return_value = 1
                utils.handling_mounting(opt_emerge_nonlocal_with_1g)


def test_handling_mounting_else(opt_emerge_nonlocal_with_1g):
    from pyerge import utils
    with mock.patch('pyerge.utils.size_of_mounted_tmpfs') as size_of_mounted_tmpfs_mock:
        with mock.patch('pyerge.utils.convert2blocks') as convert2blocks_mock:
            with mock.patch('pyerge.utils.is_tmpfs_mounted') as is_tmpfs_mounted_mock:
                is_tmpfs_mounted_mock.return_value = True
                size_of_mounted_tmpfs_mock.return_value = 1
                convert2blocks_mock.return_value = 1
                utils.handling_mounting(opt_emerge_nonlocal_with_1g)
