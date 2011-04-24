# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=2

DESCRIPTION="Lightweight FOX music collection manager and player"
HOMEPAGE="http://gogglesmm.googlecode.com/"
SRC_URI="http://${PN}.googlecode.com/files/${P}.tar.bz2"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE="asf dbus gcrypt mp4"

RDEPEND="dev-db/sqlite:3
	media-libs/taglib[asf?,mp4?]
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
	if use gcrypt ; then
		extraconf="--with-md5=gcrypt"
	else
		extraconf="--with-md5=internal"
	fi

	econf $extraconf $(use_with dbus)
}

src_install() {
	emake DESTDIR="${D}" install || die

	dodoc AUTHORS README || die
}
