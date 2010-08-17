# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3

inherit python
DESCRIPTION="A versatile and extensible tiling manager for EWHM and *box WMs"
HOMEPAGE="http://pytyle.com"
SRC_URI="ftp://foo.bar.com/${P}.tar.gz"
LICENSE="GPL-3"

SLOT="0"

KEYWORDS="~amd64 ~x86"

IUSE="gnome X"

# Build-time dependencies, such as
#    ssl? ( >=dev-libs/openssl-0.9.6b )
#    >=dev-lang/perl-5.6.1-r1
# It is advisable to use the >= syntax show above, to reflect what you
# had installed on your system when you tested the package.  Then
# other users hopefully won't be caught without the right version of
# a dependency.
DEPEND=""

RDEPEND="dev-python/python-xlib"

src_install(){
	$(python_get_sitedir)

