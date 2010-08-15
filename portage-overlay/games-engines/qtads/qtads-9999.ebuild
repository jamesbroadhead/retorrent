# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI="2"

inherit flag-o-matic games git qt4-r2

EGIT_REPO_URI="git://${PN}.git.sourceforge.net/gitroot/${PN}/${PN}"

DESCRIPTION="Qt-based GUI interpreter for TADS 2 and TADS 3 text adventures"
HOMEPAGE="http://qtads.sourceforge.net/"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS=""
IUSE=""

DEPEND="x11-libs/qt-gui:4
	x11-libs/qt-qt3support:4"
RDEPEND="${DEPEND}"

DOCS="AUTHORS BUGS CREDITS INSTALL NEWS PORTABILITY QTADS_LICENSE_NOTE_TADS2 QTADS_LICENSE_NOTE_TADS3 SOURCE_README README TIPS TODO"

src_unpack() {
	git_src_unpack
}

src_configure() {
	# Needed for the TADS3 VM (see INSTALL)
	append-flags -fno-strict-aliasing

	# Install docs to $T for the moment. dodoc will deal with them later
	eqmake4 BIN_INSTALL=/usr/games/bin DOC_INSTALL="${WORKDIR}" DATA_INSTALL=/usr/share
}

src_install() {
	qt4-r2_src_install

	doman qtads.6.gz || die

	make_desktop_entry qtads QTads
	prepgamesdirs
}
