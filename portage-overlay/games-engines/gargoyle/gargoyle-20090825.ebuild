# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

# TODO LATER:
# Create ebuilds for unpatched interpreters and package separately
# 	games-engines/frotz interpreter is already in portage 
# 	games-engines/frobtads is in portage, not sure if it can replace
#			included tads2/tads3 interpreter. 

EAPI=2

inherit eutils games versionator

# TODO: Better versioning, but currently need to keep 8-digit, \
#		so it's >games-engines/gargoyle-20060917-r1, in portage
MY_PV=${PV:0:4}-${PV:4:2}-${PV:6:2}
MY_P=${PN}-${MY_PV}

DESCRIPTION="An interactive fiction (IF) player supporting all major formats"
HOMEPAGE="http://ccxvii.net/gargoyle/"
SRC_URI="http://garglk.googlecode.com/files/${MY_P}-sources.zip"

LICENSE="BSD gargoyle hugo luximono GPL-2"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE="-debug -fmod sdl"

RDEPEND="dev-libs/glib:2
	media-libs/freetype:2
	media-libs/jpeg
	media-libs/libpng
	sys-libs/zlib
	x11-libs/gtk+:2
	fmod? ( media-libs/fmod )
	sdl? (
		media-libs/libvorbis
		media-libs/sdl-mixer
		media-libs/smpeg
	)"

DEPEND="${RDEPEND}
	app-arch/unzip
	dev-util/ftjam"

src_prepare() {
	# TODO: File upstream bug to remove hardcoded path
	sed -i -e 's|/etc|${GAMES_SYSCONFDIR}|' garglk/config.c || die

	# TODO: Clean this up 
	if use debug ; then
		JAMARGS="-sBUILD=DEBUG"
		OPTIMold="OPTIM = -g ;"
		OPTIMnew="OPTIM = -g "
	else 
		JAMARGS=""	
		OPTIMold="OPTIM = -O2 ;"
		OPTIMnew="OPTIM = "
	fi
	
	# Enable custom cflags
	OPTIMnew="$OPTIMnew $CFLAGS ;"
	sed -i -e s/"$OPTIMold"/"$OPTIMnew"/ Jamrules || die

	# FMOD is disabled by default
	if use fmod ; then
		JAMARGS="$JAMARGS -sUSEFMOD=yes"	
	fi
	# SDL is enabled by default
	if ! use sdl; then
		JAMARGS="$JAMARGS -sUSESDL=no"	
	fi
	
	edos2unix garglk/garglk.ini

	INTERPRETERS=(advsys agility alan2 alan3 frotz geas git glulxe hugo 
			jacl level9 magnetic nitfol scare tadsr)

	for interpreter in ${INTERPRETERS[@]} ; do
		echo Parsing $interpreter	
		sed -i -e s/"${interpreter}"/"gargoyle-${interpreter}"/ \
			garglk/launcher.sh	|| die
	done
		
}

src_compile() {
	jam $JAMARGS || die
}

src_install() {
	jam install || die

	insinto "${GAMES_SYSCONFDIR}"
	newins garglk/garglk.ini garglk.ini || die

	cd build/dist || die
	dogameslib libgarglk.so || die

	insinto "${GAMES_PREFIX}/libexec/${PN}"
	insopts -m0755

	for interpreter in ${INTERPRETERS[@]} ; do
		doins ${interpreter} || die
		dosym "${GAMES_PREFIX}/libexec/${PN}/${interpreter}" \
			"${GAMES_BINDIR}/${PN}-${interpreter}" || die
	done

	dogamesbin gargoyle || die
}
