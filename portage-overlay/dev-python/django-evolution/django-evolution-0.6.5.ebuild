# Copyright 1999-2011 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=2

SUPPORT_PYTHON_ABIS=1

inherit distutils python

DESCRIPTION="Track changes in database models over time, and update the db to reflect them"
HOMEPAGE="http://code.google.com/p/django-evolution/"
SRC_URI="http://pypi.python.org/packages/source/d/django_evolution/django_evolution-${PV}.tar.gz"

LICENSE="BSD"
SLOT="0"
KEYWORDS="~amd64 ~x86"
IUSE=""

RDEPEND="dev-python/django"

src_prepare() {
	rm -r tests || die
	distutils_src_prepare
}
