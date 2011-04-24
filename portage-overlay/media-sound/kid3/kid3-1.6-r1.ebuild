# Copyright 1999-2010 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo-x86/media-sound/kid3/kid3-1.4.ebuild,v 1.5 2010/07/21 13:03:05 fauli Exp $

EAPI=3
inherit kde4-base

DESCRIPTION="A simple tag editor for KDE"
HOMEPAGE="http://kid3.sourceforge.net/"
SRC_URI="mirror://sourceforge/kid3/${P}.tar.gz"

LICENSE="GPL-2"
SLOT="4"
KEYWORDS="amd64 ~ppc ~ppc64 x86 ~x86-fbsd"
IUSE="flac +handbook mp3 mp4 +musicbrainz +taglib ogg"

RDEPEND="
	flac? ( media-libs/flac[cxx]
		media-libs/libvorbis )
	mp3? ( media-libs/id3lib )
	mp4? ( media-libs/libmp4v2 )
	musicbrainz? ( media-libs/musicbrainz:3
		media-libs/tunepimp )
	ogg? ( media-libs/libvorbis )
	taglib? ( media-libs/taglib )"
DEPEND="${RDEPEND}"

src_configure() {
	# -DWITH_TUNEPIMP works, but uses the MBz RDF WebService which is deprecated
	# Details: http://musicbrainz.org/doc/Web_Service
	# Upstream bug report:
	# http://sourceforge.net/tracker/?func=detail&aid=3216188&group_id=70849&atid=529221
	epatch "${FILESDIR}"/kid3-id3form-understandability.patch

	mycmakeargs+=(
		$(cmake-utils_use_with flac FLAC)
		$(cmake-utils_use_with mp3 ID3LIB)
		$(cmake-utils_use_with mp4 MP4V2)
		$(cmake-utils_use_with musicbrainz TUNEPIMP)
		$(cmake-utils_use_with taglib TAGLIB)
		"-DWITH_TUNEPIMP=OFF"
	)

	if use flac; then
		mycmakeargs+=( "-DWITH_VORBIS=ON" )
	else
		mycmakeargs+=( $(cmake-utils_use_with ogg VORBIS) )
	fi

	kde4-base_src_configure
}