from pytest import fixture


@fixture
def str_no_sync():
    return """1548194358:  === sync
1548194358: >>> Syncing repository 'gentoo' into '/usr/portage'...
1548194361: >>> Starting rsync with rsync://[2a01:90:200:10::1a]/gentoo-portage"""


@fixture
def str_sync():
    return """1548194361: >>> Starting rsync with rsync://[2a01:90:200:10::1a]/gentoo-portage
1548194466: === Sync completed for gentoo
1548194466:  *** terminating."""


@fixture
def str_curr():
    return """1571086865:  *** emerge --nospinner --oneshot sys-kernel/linux-firmware
1571086944:  >>> emerge (1 of 1) sys-kernel/linux-firmware-20191008 to /
1571086944:  === (1 of 1) Cleaning (sys-kernel/linux-firmware-20191008::/usr/portage/sys-kernel/linux-firmware/linux-firmware-20191008.ebuild)
1571086985:  === (1 of 1) Compiling/Merging (sys-kernel/linux-firmware-20191008::/usr/portage/sys-kernel/linux-firmware/linux-firmware-20191008.ebuild)
1571086996:  === (1 of 1) Merging (sys-kernel/linux-firmware-20191008::/usr/portage/sys-kernel/linux-firmware/linux-firmware-20191008.ebuild)
1571087012:  >>> AUTOCLEAN: sys-kernel/linux-firmware:0
1571087012:  === Unmerging... (sys-kernel/linux-firmware-20191004)"""


@fixture
def str_curr_empty():
    return """1571086865:  *** emerge --nospinner --oneshot sys-kernel/linux-firmware
1571086944:  >>> emerge (1 of 1) sys-kernel/linux-firmware-20191008 to /
1571086944:  === (1 of 1) Cleaning (sys-kernel/linux-firmware-20191008::/usr/portage/sys-kernel/linux-firmware/linux-firmware-20191008.ebuild)
1571086996:  === (1 of 1) Merging (sys-kernel/linux-firmware-20191008::/usr/portage/sys-kernel/linux-firmware/linux-firmware-20191008.ebuild)
1571087012:  >>> AUTOCLEAN: sys-kernel/linux-firmware:0
1571087012:  === Unmerging... (sys-kernel/linux-firmware-20191004)"""


@fixture
def str_dl_gt_0():
    return """[ebuild     U  ] xfce-extra/thunar-archive-plugin-0.4.0::gentoo [0.3.1-r3::gentoo] 342 KiB
[ebuild     U  ] xfce-extra/thunar-shares-plugin-0.3.0::gentoo [0.2.0_p20101105-r1::gentoo] 333 KiB
[ebuild     U  ] xfce-base/xfce4-meta-4.14-r1::gentoo [4.12-r1::gentoo] USE="svg upower%* -minimal" 0 KiB

Total: 44 packages (42 upgrades, 2 new), Size of downloads: 283,699 KiB
"""

# todo: add correct printout
@fixture
def str_dl_eq_0():
    return """[ebuild     U  ] xfce-extra/thunar-archive-plugin-0.4.0::gentoo [0.3.1-r3::gentoo] 342 KiB
[ebuild     U  ] xfce-extra/thunar-shares-plugin-0.3.0::gentoo [0.2.0_p20101105-r1::gentoo] 333 KiB
[ebuild     U  ] xfce-base/xfce4-meta-4.14-r1::gentoo [4.12-r1::gentoo] USE="svg upower%* -minimal" 0 KiB

Total: 44 packages (42 upgrades, 2 new), Size of downloads: 0 KiB
"""

# todo: add correct printout
@fixture
def str_dl_unknown():
    return """[ebuild     U  ] xfce-extra/thunar-archive-plugin-0.4.0::gentoo [0.3.1-r3::gentoo] 342 KiB
[ebuild     U  ] xfce-extra/thunar-shares-plugin-0.3.0::gentoo [0.2.0_p20101105-r1::gentoo] 333 KiB
[ebuild     U  ] xfce-base/xfce4-meta-4.14-r1::gentoo [4.12-r1::gentoo] USE="svg upower%* -minimal" 0 KiB
"""


@fixture
def str_eut():
    return """[ebuild     U  ] xfce-base/xfdesktop-4.14.1::gentoo [4.12.4::gentoo] USE="libnotify thunar -debug" 1,498 KiB
[ebuild     U  ] xfce-extra/thunar-archive-plugin-0.4.0::gentoo [0.3.1-r3::gentoo] 342 KiB
[ebuild     U  ] xfce-extra/thunar-shares-plugin-0.3.0::gentoo [0.2.0_p20101105-r1::gentoo] 333 KiB
[ebuild     U  ] xfce-base/xfce4-meta-4.14-r1::gentoo [4.12-r1::gentoo] USE="svg upower%* -minimal" 0 KiB

!!! Error: couldn't get previous merge of libXpresent; skipping...

Estimated update time: 1 hour, 9 minutes.
"""
