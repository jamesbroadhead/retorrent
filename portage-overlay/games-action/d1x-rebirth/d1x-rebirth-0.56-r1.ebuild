# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo-x86/games-action/d1x-rebirth/d1x-rebirth-0.56.ebuild,v 1.1 2010/10/14 04:17:02 mr_bones_ Exp $

EAPI=2
inherit eutils scons-utils games

DESCRIPTION="Descent Rebirth - enhanced Descent 1 engine"
HOMEPAGE="http://www.dxx-rebirth.de/"
SRC_URI="mirror://sourceforge/dxx-rebirth/${PN}_v${PV}-src.tar.gz
	applecd? ( http://www.dxx-rebirth.com/download/dxx/res/d1xr-mac-sounds.zip )
	hires? ( http://www.dxx-rebirth.com/download/dxx/res/d1xr-hires.zip )
	music? ( http://www.dxx-rebirth.com/download/dxx/res/d1xr-sc55-music.zip )
	linguas_de? (
		http://www.dxx-rebirth.com/download/dxx/res/d1xr-briefings-ger.zip )"

LICENSE="D1X GPL-2 as-is"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE="applecd cdinstall +hires +music ipv6 linguas_de opengl"

RDEPEND="opengl? ( virtual/opengl virtual/glu )
	dev-games/physfs[hog,zip]
	media-libs/libsdl[audio,opengl?,video]
	media-libs/sdl-mixer
	cdinstall? ( games-action/descent1-data )"
# D1X-Rebirth currently crashes on quit with the demo data.
# http://dxx-rebirth.com/frm/showthread.php?tid=782
#	!cdinstall? ( games-action/descent1-demodata )"

S=${WORKDIR}/${PN}_v${PV}-src

src_prepare() {
	sed -i -e "/lflags = /s/$/ + env['LINKFLAGS']/" SConstruct || die
}

src_compile() {
	escons \
		verbosebuild=1 \
		sharepath="${GAMES_DATADIR}/d1x" \
		sdlmixer=1 \
		$(use_scons debug) \
		$(use_scons !opengl sdl_only) \
		$(use_scons ipv6) \
		|| die
}

src_install() {
	edos2unix INSTALL.txt README.txt
	dodoc INSTALL.txt README.txt || die

	insinto "${GAMES_DATADIR}/d1x"

	# these zip files don't need to be extracted
	if use applecd ; then
		doins "${DISTDIR}"/d1xr-mac-sounds.zip || die
	fi

	if use linguas_de ; then
		doins "${DISTDIR}"/d1xr-briefings-ger.zip || die
	fi

	if use hires ; then
		doins "${DISTDIR}"/d1xr-hires.zip || die
	fi

	if use music ; then
		doins "${DISTDIR}"/d1xr-sc55-music.zip || die
	fi

	doicon "${S}/${PN}.xpm" || die

	if use opengl ; then
		newgamesbin d1x-rebirth-gl d1x-rebirth || die
	else
		newgamesbin d1x-rebirth-sdl d1x-rebirth || die
	fi
	make_desktop_entry d1x-rebirth "Descent 1 Rebirth" || die
	prepgamesdirs || die
}

pkg_postinst() {
	games_pkg_postinst
	if ! use cdinstall ; then
		echo
		elog "To play the full game, you need to copy data"
		elog "files from an original Descent installation to:"
		elog "${GAMES_DATADIR}/d1x. Mount the CD and merge:"
		elog "games-action/descent1-data or read "
		elog "/usr/share/doc/${PF}/INSTALL.txt for more info."
		echo
	fi
}
