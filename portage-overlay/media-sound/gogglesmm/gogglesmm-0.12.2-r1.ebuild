# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=2

inherit eutils

DESCRIPTION="Lightweight FOX music collection manager and player"
HOMEPAGE="http://gogglesmm.googlecode.com/"
SRC_URI="http://${PN}.googlecode.com/files/${P}.tar.bz2"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64 ~x86"
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

	# Upstream patch to fix parallel builds. Won't be needed >=0.12.3
	epatch "${FILESDIR}"/gogglesmm-parallel-make.patch || die
}

src_configure() {
	local extraconf=""

	if use gcrypt ; then
		extraconf="--with-md5=gcrypt"
	else
		extraconf="--with-md5=internal"
	fi

	econf ${extraconf} $(use_with dbus)
}

src_install() {
	make DESTDIR="${D}" install || die

	dodoc AUTHORS README || die
}

pkg_postinst() {
	einfo "For asf and/or mp4 tag support, build "
	einfo "    media-libs/taglib with USE=\"asf mp4\""
}
