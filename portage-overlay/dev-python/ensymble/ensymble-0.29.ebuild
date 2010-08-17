# Copyright 1999-2007 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

PYTHON_DEPEND="2"

inherit distutils

DESCRIPTION="Collection of tools for making Python for S60 programs."
HOMEPAGE="http://code.google.com/p/ensymble/"
SRC_URI="http://${PN}.googlecode.com/files/${P}.tar.gz"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

DEPEND=""
RDEPEND="${DEPEND}
	dev-libs/openssl"

