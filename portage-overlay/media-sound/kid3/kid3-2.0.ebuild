# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=4
KDE_LINGUAS="cs de es et fi fr it nl pl ru tr zh_TW"
KDE_REQUIRED="optional"
KDE_HANDBOOK="optional"
inherit kde4-base

DESCRIPTION="A simple tag editor for KDE"
HOMEPAGE="http://kid3.sourceforge.net/"
SRC_URI="mirror://sourceforge/kid3/${P}.tar.gz"

LICENSE="GPL-2"
SLOT="4"
KEYWORDS="~amd64 ~ppc ~ppc64 ~x86 ~x86-fbsd"
IUSE="flac kde id3lib mp4 musicbrainz +taglib vorbis"

RDEPEND="
	flac? (
		media-libs/flac[cxx]
		media-libs/libvorbis
	)
	id3lib? ( media-libs/id3lib )
	mp4? ( media-libs/libmp4v2 )
	musicbrainz? ( media-libs/musicbrainz:3
		media-libs/tunepimp )
	taglib? ( media-libs/taglib )
	vorbis? ( media-libs/libvorbis )"
DEPEND="${RDEPEND}"

REQUIRED_USE="flac? ( vorbis )"

src_prepare() {
	kde4-base_src_prepare
}

src_configure() {
	# -DWITH_TUNEPIMP works, but uses the MBz RDF WebService which is deprecated
	# Details: http://musicbrainz.org/doc/Web_Service
	# Upstream bug report:
	# http://sourceforge.net/tracker/?func=detail&aid=3216188&group_id=70849&atid=529221

	local mycmakeargs=(
		$(cmake-utils_use_with flac)
		$(cmake-utils_use_with id3lib ID3LIB)
		$(cmake-utils_use_with kde)
		$(cmake-utils_use_with mp4 MP4V2)
		$(cmake-utils_use_with musicbrainz TUNEPIMP)
		$(cmake-utils_use_with vorbis)
		$(cmake-utils_use_with taglib)
	)

	kde4-base_src_configure
}
