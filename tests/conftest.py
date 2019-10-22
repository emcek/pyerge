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


@fixture
def str_eut_unknown():
    return """[ebuild     U  ] xfce-base/xfdesktop-4.14.1::gentoo [4.12.4::gentoo] USE="libnotify thunar -debug" 1,498 KiB
[ebuild     U  ] xfce-extra/thunar-archive-plugin-0.4.0::gentoo [0.3.1-r3::gentoo] 342 KiB
[ebuild     U  ] xfce-extra/thunar-shares-plugin-0.3.0::gentoo [0.2.0_p20101105-r1::gentoo] 333 KiB
[ebuild     U  ] xfce-base/xfce4-meta-4.14-r1::gentoo [4.12-r1::gentoo] USE="svg upower%* -minimal" 0 KiB

!!! Error: couldn't get previous merge of libXpresent; skipping...
"""


@fixture
def orginal_html_xml():
    html = b'<?xml version="1.0" encoding="UTF-8"?>\n<rdf:RDF xmlns="http://purl.org/rss/1.0/"\n  ' \
           b'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n  ' \
           b'xmlns:content="http://purl.org/rss/1.0/modules/content/"\n  ' \
           b'xmlns:dc="http://purl.org/dc/elements/1.1/"\n  ' \
           b'xmlns:image="http://purl.org/rss/1.0/modules/image/"\n  ' \
           b'xmlns:slash="http://purl.org/rss/1.0/modules/slash/"\n  ' \
           b'xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"\n  ' \
           b'xmlns:taxo="http://purl.org/rss/1.0/modules/taxonomy/"\n  ' \
           b'xmlns:trackback="http://madskills.com/public/xml/rss/module/trackback/">\n' \
           b'<channel rdf:about="https://security.gentoo.org/glsa">\n    ' \
           b'<title>Gentoo Linux security advisories</title>\n    ' \
           b'<link>https://security.gentoo.org/glsa</link>\n    ' \
           b'<description>This feed contains new Gentoo Linux security advisories. ' \
           b'Contact security@gentoo.org with questions.</description>\n' \
           b'<items>\n      <rdf:Seq>\n' \
           b'<rdf:li resource="https://security.gentoo.org/glsa/201904-25"/>\n' \
           b'<rdf:li resource="https://security.gentoo.org/glsa/201904-24"/>\n' \
           b'<rdf:li resource="https://security.gentoo.org/glsa/201904-23"/>\n' \
           b'</items>\n    <dc:date>2019-04-24T00:00:00+00:00</dc:date>\n  </channel>\n' \
           b'<item rdf:about="https://security.gentoo.org/glsa/201904-25">\n    ' \
           b'<title>GLSA 201904-25: QEMU: Multiple vulnerabilities</title>\n    ' \
           b'<link>https://security.gentoo.org/glsa/201904-25</link>\n    ' \
           b'<dc:date>2019-04-24T00:00:00+00:00</dc:date>\n  </item>\n' \
           b'<item rdf:about="https://security.gentoo.org/glsa/201904-24">\n    ' \
           b'<title>GLSA 201904-24: Ming: Multiple vulnerabilities</title>\n    ' \
           b'<link>https://security.gentoo.org/glsa/201904-24</link>\n    ' \
           b'<dc:date>2019-04-24T00:00:00+00:00</dc:date>\n  </item>\n' \
           b'<item rdf:about="https://security.gentoo.org/glsa/201904-23">\n    ' \
           b'<title>GLSA 201904-23: GLib: Multiple vulnerabilities</title>\n    ' \
           b'<link>https://security.gentoo.org/glsa/201904-23</link>\n    ' \
           b'<dc:date>2019-04-22T00:00:00+00:00</dc:date>\n  </item>\n' \
           b'</rdf:RDF>'
    return html


@fixture()
def html_xlm_as_str():
    return """
<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns="http://purl.org/rss/1.0/"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:image="http://purl.org/rss/1.0/modules/image/"
  xmlns:slash="http://purl.org/rss/1.0/modules/slash/"
  xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
  xmlns:taxo="http://purl.org/rss/1.0/modules/taxonomy/"
  xmlns:trackback="http://madskills.com/public/xml/rss/module/trackback/">
  <channel rdf:about="https://security.gentoo.org/glsa">
    <title>Gentoo Linux security advisories</title>
    <link>https://security.gentoo.org/glsa</link>
    <description>This feed contains new Gentoo Linux security advisories. Contact security@gentoo.org with questions.</description>
    <items>
      <rdf:Seq>
        <rdf:li resource="https://security.gentoo.org/glsa/201904-23"/>
        <rdf:li resource="https://security.gentoo.org/glsa/201904-22"/>
      </rdf:Seq>
    </items>
    <dc:date>2019-04-24T00:00:00+00:00</dc:date>
  </channel>
  <item rdf:about="https://security.gentoo.org/glsa/201904-23">
    <title>GLSA 201904-23: GLib: Multiple vulnerabilities</title>
    <link>https://security.gentoo.org/glsa/201904-23</link>
    <dc:date>2019-04-22T00:00:00+00:00</dc:date>
  </item>
  <item rdf:about="https://security.gentoo.org/glsa/201904-22">
    <title>GLSA 201904-22: OpenDKIM: Root privilege escalation</title>
    <link>https://security.gentoo.org/glsa/201904-22</link>
    <dc:date>2019-04-22T00:00:00+00:00</dc:date>
  </item>
</rdf:RDF>
"""
