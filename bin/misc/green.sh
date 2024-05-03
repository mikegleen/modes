#!/bin/zsh
set -e
green () {
    print -P "%F{green}${1}%f\n"
}
#
echo ----------------------------------------------------
# The input file was created manually to remove Mottisfont from JB145
green "Step 0. Add JB315 to the Mottisfont exhibition."
