#!/bin/zsh
find ../collection/aawebimgs -name "*${1:u}.jpg" -exec ls -l {} \;
find /Users/mlg/Pictures/VueScan -name "*${1:u}.jpg" -exec ls -l {} \;
find ../scans -name "*${1:u}.jpg" -exec ls -l {} \;
echo ---
