# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo-x86/net-news/rawdog/rawdog-2.13.ebuild,v 1.9 2011/01/07 00:32:29 ranger Exp $

EAPI="2"

# TODO: TEST with python-3

PYTHON_DEPEND="2"
SUPPORT_PYTHON_ABIS="1"
RESTRICT_PYTHON_ABIS="3.*"

inherit distutils python

DESCRIPTION="RSS Broadcatcher for podcasts, videocasts, and torrent feeds"
HOMEPAGE="http://code.google.com/p/rssdler"
SRC_URI="http://rssdler.googlecode.com/files/${P}.tar.gz"
LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

DEPEND="dev-python/feedparser"
RDEPEND=""

DOCS="README"
PYTHON_MODNAME="${PN}"

# Version number without separators
MY_P="${PN}${PV//.}"
S="${WORKDIR}/${MY_P}"

src_compile() {
	distutils_src_compile
}

src_install() {
	distutils_src_install

	newman "${FILESDIR}/rssdler.man" rssdler.1 || die
}

pkg_postinst() {
	einfo 'If you encounter problems with referers or redirects, installing'
	einfo '  dev-python/mechanize is recommended. See man rssdler for more'
}
