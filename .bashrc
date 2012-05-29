#!/bin/sh

if [ -f /etc/bashrc ]; then
    . /etc/bashrc   # --> Read /etc/bashrc, if present.
fi

# Use bash-completion, if available
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

# Set path to include user scripts
export PATH="${PATH}:~/bin/"

# Use cdpath to setup some shortcuts
export CDPATH=.:/home/sgordon/Documents/books/redhat/

# Set bash to use vi style key binds, I will regret this.
set -o vi

# Aliases for adding some colour
alias diff="/usr/bin/colordiff"
alias grep="/bin/grep --color"
alias zgrep="/usr//bin/zgrep --color"
alias less="/usr/bin/less -R"
alias more="/usr/bin/more -R"

# Alias to include ssh options, allows me to keep these in my 'travelling' 
# config rather than my SSH configs on specific machines.
alias ssh="ssh -o VisualHostKey=yes"

#alias svndiff="svn diff ${@} | colordiff"

# Default xmllint to DocBook 4.5 DTD
alias xmllint="xmllint --dtdvalid http://www.oasis-open.org/docbook/xml/4.5/docbookx.dtd"

# Alias wget to graphically notify
#alias wget="wget ${@} | /usr/bin/notify-send "Download complete!""
alias wget="wget ${@}"

# Modify history search keys, entering 'sudo' and pressing up returns last
# command run that started with sudo for example.
bind '"\e[A"':history-search-backward
bind '"\e[B"':history-search-forward

# Some further history shenanigans, append to the history file 
# (rather than overwrite it) to support multiple sessions. Then
# set the prompt to save history after a command is executed,
# not when the session ends.
shopt -s histappend
if [ "${PROMPT_COMMAND}" ]; then
	export PROMPT_COMMAND="${PROMPT_COMMAND}; history -a; history -n"
else
	export PROMPT_COMMAND="history -a; history -n"
fi

# Ignore blank/repeated lines in bash history.
export HISTCONTROL=ignoreboth
export HISTSIZE=1000

# Set vim as default editor
export SVN_EDITOR="/usr/bin/vim"
export SVN_MERGE="/usr/bin/meld"
export EDITOR="/usr/bin/vim"

# Speed up beagle indexing
export BEAGLE_EXCERCISE_THE_DOG=1
PATH=$PATH:/usr/share/maven2/bin
