#!/bin/zsh
#
# convert <part /> to <part>image</part>
#
set -e
INXML=prod_update/normal/2024-09-20_merged_accessions.xml
OUTFULLXML=prod_update/normal/2024-09-23_part_image.xml
OUTDELTAXML=prod_delta/normal/2024-09-23_part_image.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
python src/once/x055_part.py $INXML $OUTFULLXML -a
python src/once/x055_part.py $INXML $OUTDELTAXML
bin/syncdelta.sh
bin/syncupdate.sh
