# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=3

PYTHON_DEPEND="2"
SUPPORT_PYTHON_ABIS="1"
RESTRICT_PYTHON_ABIS="3.*"

inherit distutils python versionator

MY_PN=ReviewBoard
#MY_PV=$(replace_version_separator '_' '') # only needed for beta release
MY_PV="1.6rc1"
MY_P=${MY_PN}-${MY_PV}

DESCRIPTION="A web-based tool for tracking of pending code changes to help code reviews"
HOMEPAGE="http://www.reviewboard.org/"
SRC_URI="http://downloads.${PN}.org/releases/${MY_PN}/$(get_version_component_range 1-2)/${MY_P}.tar.gz"

LICENSE="MIT"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

RDEPEND=">=dev-python/django-evolution-0.64
	>=dev-python/Djblets-0.6.8
	dev-python/flup
	dev-python/imaging
	dev-python/paramiko
	dev-python/pygments
	dev-python/python-memcached
	dev-python/pytz
	dev-python/recaptcha-client
	|| ( dev-python/django[sqlite] dev-python/django[mysql] dev-python/django[postgres] )
	|| ( ( www-apache/mod_wsgi www-servers/apache ) virtual/httpd-fastcgi )"

S=${WORKDIR}/${MY_P}

pkg_postinst() {
	distutils_pkg_postinst
	elog "You must install any VCS tool you wish ${PN} to support."
	elog "dev-util/cvs, dev-vcs/git, dev-vcs/mercurial or dev-util/subversion."
	elog
	elog "Enable the mysql, postgres or sqlite USEflag on dev-python/django"
	elog "to use the corresponding database backend."
	elog
	elog "For speed and responsiveness, consider installing net-misc/memcached"
	elog "and dev-python/python-memcached"
}
