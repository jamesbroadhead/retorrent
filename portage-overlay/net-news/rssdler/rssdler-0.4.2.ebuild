# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo-x86/net-news/rawdog/rawdog-2.13.ebuild,v 1.9 2011/01/07 00:32:29 ranger Exp $

#EAPI="3"

# TODO: TEST with python-3

PYTHON_DEPEND="2"
SUPPORT_PYTHON_ABIS="1"
RESTRICT_PYTHON_ABIS="3.*"

inherit distutils

DESCRIPTION="RSS Broadcatcher for podcasts, videocasts, and torrent feeds"
HOMEPAGE="http://code.google.com/p/rssdler"
SRC_URI="http://code.google.com/p/${PN}/downloads/detail?name=${P}.tar.gz"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

DEPEND=""
RDEPEND=""

DOCS="README"
PYTHON_MODNAME="${PN}"

# Version number without separators
MY_P="${PN}${PV//.}"

src_unpack() {
	ls
	echo ${MY_P}
	cd "${MY_P}"
	python_copy_sources
}
