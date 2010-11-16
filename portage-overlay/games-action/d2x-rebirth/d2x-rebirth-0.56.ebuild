# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI="2"

inherit games scons-utils

DESCRIPTION="Descent Rebirth - enhanced Descent 2 engine"
HOMEPAGE="http://www.dxx-rebirth.com/"
SRC_URI="mirror://sourceforge/dxx-rebirth/${PN}_v${PV}-src.tar.gz
		linguas_de? ( http://www.dxx-rebirth.com/download/dxx/res/d2xr-briefings-ger.zip )
		music? ( http://www.dxx-rebirth.com/download/dxx/res/d2xr-sc55-music.zip )"
LICENSE="D1X GPL-2 as-is"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE="debug ipv6 linguas_de music opengl"

DEPEND="app-arch/unzip
	dev-games/physfs[hog,mvl,zip]
	media-libs/libsdl[audio,opendl?,video]
	media-libs/sdl-mixer
	opengl? ( virtual/opengl virtual/glu )"
RDEPEND="${DEPEND}
	cdinstall? ( games-action/descent2-data )
	!cdinstall? ( games-action/descent2-demodata )"

S=${WORKDIR}/${PN}_v${PV}-src

src_compile() {
	scons ${MAKEOPTS} \
		verbosebuild=1 \
		sharepath="${GAMES_DATADIR}/d2x" \
		sdlmixer=1 \
		$(use_scons debug) \
		$(use_scons !opengl sdl_only) \
		$(use_scons ipv6)
		|| die
}

src_install() {
	edos2unix INSTALL.txt README.txt
	dodoc INSTALL.txt README.txt

	# These zip files do not need to be extracted
	insinto "${GAMES_DATADIR}/d2x"
	use linguas_de && doins "${DISTDIR}"/d2xr-briefings-ger.zip
	use music && doins "${DISTDIR}"/d2xr-sc55-music.zip
	doicon ${PN}.xpm

	if use opengl ; then
		newgamesbin d2x-rebirth-gl d2x-rebirth
	else
		newgamesbin d2x-rebirth-sdl d2x-rebirth
	fi
	make_desktop_entry d2x-rebirth "Descent 2 Rebirth" ${PN}
	prepgamesdirs
}

pkg_postinst() {
	games_pkg_postinst
	if ! use cdinstall ; then
		elog "The Descent 2 Demo data has been installed."
		elog "To play the full game enable USE=cdinstall or manually copy "
		elog "the files to ${GAMES_DATADIR}/d2x."
		elog "Read /usr/share/doc/${PF}/INSTALL.txt for details."
	fi
}
