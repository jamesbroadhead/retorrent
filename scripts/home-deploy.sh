#!/bin/bash

DEPLOYDIR="$1"

for i in $1/dot_* ; do
    dot_name="$(basename ${i})"
    dot_path="$(dirname ${i})/${dot_name}"
    newname="$(basename ${i/dot_/.})"
    newpath="${HOME}/${newname}"

    if [ -e "${newpath}" ] || [ -L "${newpath}" ] ; then 
	
	# broken symlink in place
	if ! [ -f "${HOME}/$newname" ] && [ -L "${HOME}/$newname" ] ; then 
		rm "$newpath"
	# not a symlink pointing to the correct location
	elif ! [ "$(readlink ${HOME}/${newname})" = "${dot_path}" ] ; then
		echo "$newname already existed! $newname --> ${newname}.bak"
		mv -i "${HOME}/${newname}" "${HOME}/${newname}.bak"
	
	# for simplicity, remove symlinks pointing to the correct location
   	else
		rm $newpath
	fi
    fi

    ln -s "$dot_path" ${HOME}/${newname}
done

echo "==============="
echo " need manual attention: "
for i in $1/inside* ; do
	echo "$i"
done
