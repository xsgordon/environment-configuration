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
alias xmllint-db4="xmllint --dtdvalid http://www.oasis-open.org/docbook/xml/4.5/docbookx.dtd"
alias xmllint-db5="xmllint --relaxng http://docbook.org/xml/5.0/rng/docbook.rng" 

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

# Set Go path
export GOPATH="/home/`basename ~`/gocode"

# Ansible roles directory for galaxy
export ANSIBLE_ROLES_PATH=~/roles
if [ ! -d "${ANSIBLE_ROLES_PATH}" ]; then
    mkdir "${ANSIBLE_ROLES_PATH}"
fi

# Include git branch in prompt. Blatantly copied from:
# https://techcommons.stanford.edu/topics/git/show-git-branch-bash-prompt
function parse_git_branch {
  git branch --no-color 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/(\1)/'
}

function proml {
  local BLUE="\[\033[0;34m\]"
  local RED="\[\033[0;31m\]"
  local LIGHT_RED="\[\033[1;31m\]"
  local GREEN="\[\033[0;32m\]"
  local LIGHT_GREEN="\[\033[1;32m\]"
  local WHITE="\[\033[1;37m\]"
  local LIGHT_GRAY="\[\033[0;37m\]"
  case $TERM in
    xterm*)
      TITLEBAR='\[\033]0;\u@\h:\w\007\]'
      ;;
    *)
      TITLEBAR=""
      ;;
  esac

  PS1="${TITLEBAR}\
\u@\h:\w$WHITE\$(parse_git_branch)\
$LIGHT_GRAY> "
  PS2='> '
  PS4='+ '
}
proml
