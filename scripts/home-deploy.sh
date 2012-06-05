#!/bin/bash

for i in ${HOME}/checkouts/twitter-home/dot_* ; do
	dot_name="$(basename ${i})"
    dot_path="$(dirname ${i})/${dot_name}"
	newname="$(basename ${i/dot_/.})"

	if [ -e ${HOME}/$newname ] && ! [ "$(readlink ${HOME}/${newname})" = "${dot_path}" ] ; then
		echo "$newname already existed --> ${newname}.bak"
		mv -i "${HOME}/${newname}" "${HOME}/${newname}.bak"
    fi
    if [ "$(readlink ${HOME}/${newname})" = "${dot_path}" ] ; then
        echo "Skipping $newname"
    else
        ln -s "$dot_path" ${HOME}/${newname}
    fi
done
