# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo-x86/net-news/rawdog/rawdog-2.13.ebuild,v 1.9 2011/01/07 00:32:29 ranger Exp $

EAPI=2

PYTHON_DEPEND="2"
SUPPORT_PYTHON_ABIS="1"
RESTRICT_PYTHON_ABIS="3.*"

inherit distutils

DESCRIPTION="Download daemon to automatically fetch objects linked to in RSS
feeds, such as podcasts or torrents"
HOMEPAGE="http://code.google.com/p/rssdler"
SRC_URI="http://${PN}.googlecode.com/files/${P}.tar.gz"
LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

DEPEND="dev-python/feedparser"
RDEPEND=""

# Version number without separators
MY_P="${PN}${PV//.}"
S="${WORKDIR}/${MY_P}"

src_install() {
	distutils_src_install

	dodoc README || die
	newman "${FILESDIR}/rssdler.man" rssdler.1 || die
}

pkg_postinst() {
	elog 'For an intial config file, run the following as a normal user:'
	elog '  $ C="${HOME}/.rssdler/config.txt"'
	elog '  $ mkdir -p `dirname $C`'
	elog '  $ ! [ -f $C ] && rssdler --comment-config > $C'
	elog '  $ nano $C'
	echo
	elog 'If you encounter problems with referers or redirects, installing'
	elog '  dev-python/mechanize is recommended. See man rssdler for more'
	echo
}
