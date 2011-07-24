# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=2

inherit mercurial

DESCRIPTION="Lightweight FOX music collection manager and player"
HOMEPAGE="http://gogglesmm.googlecode.com/"
EHG_REPO_URI="http://${PN}.googlecode.com/hg"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS=""
IUSE="dbus gcrypt"

RDEPEND="dev-db/sqlite:3
	media-libs/taglib
	media-libs/xine-lib
	net-misc/curl
	x11-libs/fox[png]
	dbus? ( sys-apps/dbus )
	gcrypt? ( dev-libs/libgcrypt )"
DEPEND="${RDEPEND}"

src_prepare() {
	sed -i -e 's:icons/hicolor/48x48/apps:pixmaps:' Makefile || die
}

src_configure() {
	local extraconf=""

	if use gcrypt ; then
		extraconf="--with-md5=gcrypt"
	else
		extraconf="--with-md5=internal"
	fi

	econf ${extraconf} $(use_with dbus)

	# Disabling parallel build until bug fixed.
	# http://code.google.com/p/gogglesmm/issues/detail?id=247
	MAKEOPTS="${MAKEOPTS} -j1"
}

src_install() {
	emake DESTDIR="${D}" install || die

	dodoc AUTHORS README || die
}

pkg_postinst() {
	elog "For asf or mp4 tag support, build "
	elog "    media-libs/taglib with USE=\"asf mp4\""
}
