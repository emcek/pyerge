# Copyright 1999-2026 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

PYTHON_COMPAT=( python3_{11..14} )
DISTUTILS_USE_PEP517=setuptools
inherit distutils-r1 pypi

DESCRIPTION="Wrapper tool for emerge - it can mount RAM disk and compile packages inside it."
HOMEPAGE="https://github.com/emcek/pyerge https://pypi.org/project/pyerge/"
LICENSE="MIT"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE="test"

RDEPEND="
        dev-python/beautifulsoup4[${PYTHON_USEDEP}]
        dev-python/lxml[${PYTHON_USEDEP}]
        sys-apps/portage
        app-portage/eix
        app-portage/genlop
        app-portage/smart-live-rebuild
        app-admin/sudo
        sys-apps/coreutils
        net-misc/iputils
"
BDEPEND="
        ${RDEPEND}
        test? (
                dev-python/pytest[${PYTHON_USEDEP}]
                dev-python/mock[${PYTHON_USEDEP}]
        )
"

EPYTEST_PLUGINS=()
distutils_enable_tests pytest

python_test() {
        py.test -v tests || die "tests fail with ${EPYTHON}"
}