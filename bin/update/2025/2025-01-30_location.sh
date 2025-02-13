#!/bin/zsh
#
#   Set LDHRM.2023.19 to 'Out for restoration'
#
set -e
INXML=2024-10-27_merged_accessions.xml
OUTXML=2025-01-30_location.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
green () {
    print -P "%F{green}$*%f"
}
yellow () {
    print -P "%F{yellow}$*%f"
}
#
yellow ----------------------------------------------------
yellow "Update the single object"
yellow ----------------------------------------------------
#
python src/location.py update -i prod_update/normal/$INXML -o prod_update/normal/$OUTXML -a \
                        --object LDHRM.2023.19 --current --location 'Out for Restoration'
#
python src/location.py update -i prod_update/normal/$INXML -o prod_make/normal/$OUTXML \
                        -j LDHRM.2023.19 -c -l 'Out for Restoration'
#
bin/syncupdate.sh
bin/syncmake.sh
