#!/bin/bash

# Date for use when naming backup files.
DATE=`date +%Y%m%d`

# Check if dot files already exist:
#  - if they do and they are files back them up; or
#  - if they do and they are links unlink them
# Then create links to the location of the checkout, this way all that is
# required in future to get the latest is to do a git pull.
for FILE in ".vimrc" ".bashrc"; do
    if [ -f "${HOME}/${FILE}" ]; then
        if [ -L "${HOME}/${FILE}" ]; then
            echo "Unlinking ${HOME}/${FILE}"
            unlink ${HOME}/${FILE}
        else
            echo "Backing up ${HOME}/${FILE} to ${HOME}/${FILE}-${DATE}.bak"
            mv ${HOME}/${FILE} ${HOME}/${FILE}-${DATE}.bak
        fi
    fi
    echo "Linking `pwd`/${FILE} ${HOME}/${FILE}"
    ln -s `pwd`/${FILE} ${HOME}/${FILE}
done

# Special casing the .vim directory, the repository contains configurations
# for various items and even entire plugins but the local working copy will
# tend to contain files that have identifying user data in them. Copy new .vim
# info into the user's ~/.vim recursively - in effect adding the new plugins.
if [ -d "${HOME}/.vim" ]; then
    echo "Recursively coping ${PWD}/.vim/* to ${HOME}/.vim"
    cp -r ${PWD}/.vim/* ${HOME}/.vim
fi
