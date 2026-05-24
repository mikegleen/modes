#!/bin/bash
#!/opt/homebrew/bin/bash
echo argv: ${0}
base="${0##*/}"   # remove directory, keep tail
root="${base%.*}"        # remove extension
echo root="$root"
echo basename "$(basename "${0%.*}")"
