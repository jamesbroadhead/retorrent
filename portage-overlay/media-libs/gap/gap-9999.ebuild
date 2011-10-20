# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=4

inherit flag-o-matic mercurial

DESCRIPTION="Gapless Audio Player Library for Goggles Musicmanager (media-sound/gogglesmm)"
HOMEPAGE="http://code.google.com/p/gogglesmm/"
EHG_REPO_URI="https://${PN}.gogglesmm.googlecode.com/hg/"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS=""
IUSE="aac alsa cdda ffmpeg flac jack mad mms musepack ogg pulseaudio samba libsamplerate vorbis"

DEPEND=">=x11-libs/fox-1.7.30
	dev-libs/glib:2	
	aac? ( media-libs/faad2 )
	alsa? ( media-libs/alsa-lib )
	cdda? ( dev-libs/libcdio )
	ffmpeg? ( media-video/ffmpeg )
	flac? ( media-libs/flac )
	jack? ( >=media-sound/jack-audio-connection-kit-0.118.0 )
	mad? ( media-libs/libmad )
	mms? ( media-libs/libmms )
	musepack? ( media-sound/musepack-tools )
	ogg? ( media-libs/libogg )
	pulseaudio? ( media-sound/pulseaudio )
	samba? ( net-fs/samba[client] )
	libsamplerate? ( media-libs/libsamplerate )
	vorbis? ( media-libs/libvorbis )"
RDEPEND="${DEPEND}"

src_prepare() {
	sed -i 's/dash/sh/' configure || die

	# patch in --shared -fPIC into config.make ?

}

src_configure() {
	econf \
		$(use_with aac faad) \
		$(use_with alsa ) \
		$(use_with cdda ) \
		$(use_with ffmpeg avcodec) \
		$(use_with flac ) \
		$(use_with jack ) \
		$(use_with mad ) \
		$(use_with mms ) \
		$(use_with musepack ) \
		$(use_with ogg ) \
		$(use_with pulseaudio pulse ) \
		$(use_with samba ) \
		$(use_with libsamplerate samplerate) \
		$(use_with vorbis ) \
		--enable-debug
		--without-rsound # not in portage or sunrise
}

src_compile() {
	append-ldflags -shared -fPIC || die

	emake
}
