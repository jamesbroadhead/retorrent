# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo-x86/games-action/descent2-data/descent2-data-1.0.ebuild,v 1.8 2010/02/10 03:46:25 josejx Exp $

inherit eutils games

MY_PV=${PV/./}

DESCRIPTION="Data files for Descent 1"
HOMEPAGE="http://www.interplay.com/games/product.asp?GameID=109"
SRC_URI=""

# See readme.txt
LICENSE="${PN}"
SLOT="0"
KEYWORDS="~amd64 ~ppc ~x86"
IUSE=""

DEPEND="!games-action/descent1-demodata"

S=${WORKDIR}
dir=
files=

pkg_setup() {
	games_pkg_setup

	need_cd="n"

	for f in {descent.hog,descent.pig,chaos.hog,chaos.msn} ; do
		if ! [ -e "${DISTDIR}/${f}" ] ; then
			up_f=`echo ${f} | tr [:lower:] [:upper:]`
			if [ -e "${DISTDIR}/${up_f}" ] ; then
				mv "${DISTDIR}/${up_f}" "${DISTDIR}/${f}"
			else
				need_cd="y"
			fi
		fi
	done
}

src_unpack() {

	if [ "${need_cd}" == "y" ] ; then
		cdrom_get_cds "descent/descent.hog"
		CDROM_DIR="${CDROM_ROOT}/descent"

		for f in {descent.hog,descent.pig,chaos.hog,chaos.msn} ; do
			up_f=`echo ${f} | tr [:lower:] [:upper:]`
			if [ -e "${CDROM_DIR}/${f}" ] ; then
				cp "${CDROM_DIR}/${f}" "${S}" || die
			elif [ -e "${CDROM_DIR}/$up_f" ] ; then
				cp "${CDROM_DIR}/${up_f}" "${S}/${f}" || die
			else
				die "File ${f} not found on the CD"
			fi
		done
	else
		# we have already checked that they exist
		mv 	"${DISTDIR}"/descent.{hog,pig} \
			"${DISTDIR}"/chaos.{hog,msn}
			"${S}" || die "Failed to move files from $DISTDIR"
	fi
}

src_install() {
	# keep the same as games-action/descent1-demodata
	insinto "${GAMES_DATADIR}/d1x"
	doins * || die "doins * failed"

	prepgamesdirs
}

pkg_postinst() {
	games_pkg_postinst

	elog "A client is needed to run the game, e.g. games-action/d2x-rebirth."
}
