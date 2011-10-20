# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=2

inherit autotools-utils mercurial

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
	media-sound/gap	
	net-misc/curl
	x11-libs/fox:1.7[png]
	dbus? ( sys-apps/dbus )
	gcrypt? ( dev-libs/libgcrypt )"
DEPEND="${RDEPEND}"

DOCS=(AUTHORS README)

src_prepare() {
	sed -i -e 's:icons/hicolor/48x48/apps:pixmaps:' Makefile || die
}

src_configure() {
	local extraconf="--with-md5=internal"

	if use gcrypt ; then
		extraconf="--with-md5=gcrypt"
	fi

	local myeconfargs=( ${extraconf} $(use_with dbus) )

	autotools-utils_src_configure
}

src_install() {
	autotools-utils_src_install
}

pkg_postinst() {
	elog "For asf and/or mp4 tag support, build "
	elog "    media-libs/taglib with USE='asf mp4'"
}
