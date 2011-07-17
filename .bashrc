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

# Share history between all open shells.
#export PROMPT_COMMAND="history -a; history -n"

# Set bash to use vi style key binds, I will regret this.
set -o vi

# Aliases for adding some colour
alias diff='/usr/bin/colordiff'
alias grep='/bin/grep --color'
alias zgrep='/usr//bin/zgrep --color'
alias less='/usr/bin/less -R'
alias more='/usr/bin/more -R'
#alias svndiff="svn diff ${@} | colordiff"

# Alias wget to graphically notify
#alias wget='wget ${@} | /usr/bin/notify-send "Download complete!"'
alias wget='wget ${@}'

# Modify history search keys, entering 'sudo' and pressing up returns last
# command run that started with sudo for example.
bind '"\e[A"':history-search-backward
bind '"\e[B"':history-search-forward

# Ignore blank/repeated lines in bash history.
export HISTCONTROL=ignoreboth

# Set vim as default editor
export SVN_EDITOR='/usr/bin/vim'
export SVN_MERGE='/usr/bin/meld'
export EDITOR='/usr/bin/vim'

# Speed up beagle indexing
export BEAGLE_EXCERCISE_THE_DOG=1
