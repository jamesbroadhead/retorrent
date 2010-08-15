# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=2

inherit eutils games

MY_PV="2008-12-25"
MY_P=${PN}-${MY_PV}
DESCRIPTION="An interactive fiction (IF) player supporting all major formats"
HOMEPAGE="http://ccxvii.net/gargoyle/"
SRC_URI="http://garglk.googlecode.com/files/${MY_P}-sources.zip"

LICENSE="BSD"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE="sdl"

RDEPEND=">=media-libs/freetype-2.1.9-r1
	>=x11-libs/gtk+-2.10.6
	>=dev-libs/glib-2.12.4-r1
	>=media-libs/jpeg-6b-r5
	>=media-libs/libpng-1.2.8
	>=sys-libs/zlib-1.2.3
	sdl? ( >=media-libs/sdl-mixer-1.2.7 >=media-libs/smpeg-0.4.4 >=media-libs/libvorbis-1.2.0 )"

DEPEND="${RDEPEND}
	dev-util/ftjam
	app-arch/unzip"

src_prepare() {
	epatch "${FILESDIR}/${P}-glk.h-patch"
	epatch "${FILESDIR}/${P}-getline-patch"

	# Fix file locations:
	sed -e "s|/usr/share/gargoyle/bin|${GAMES_PREFIX}/libexec/gargoyle|g" -i garglk/launcher.sh || die
	sed -e "s|/etc|${GAMES_SYSCONFDIR}|" -i garglk/config.c || die

	# Convert Windows newlines in ini file:
	edos2unix garglk/garglk.ini

	if ! use sdl; then
		sed -i -e 's/USESDL = yes ;/# USESDL = yes ;/' Jamrules || die
	fi

	# Allow custom CFLAGS to be used instead of just -O2:
	sed -i -e "s/-O2/${CFLAGS}/" Jamrules || die
}

src_compile() {
	jam || die
	jam install || die
}

src_install() {
	dodoc License.txt licenses/* || die

	insinto "${GAMES_SYSCONFDIR}"
	newins garglk/garglk.ini garglk.ini || die

	cd build/dist
	dogameslib libgarglk.so || die
	dogamesbin gargoyle || die

	insinto "${GAMES_PREFIX}/libexec/gargoyle"
	insopts -m0755

	local terp
	for terp in advsys agility alan2 alan3 frotz geas git glulxe hugo \
				jacl level9 magnetic nitfol scare tadsr
	do
		doins "${terp}" || die
		dosym "${GAMES_PREFIX}/libexec/gargoyle/${terp}" "${GAMES_BINDIR}/gargoyle-${terp}" || die
	done

}
