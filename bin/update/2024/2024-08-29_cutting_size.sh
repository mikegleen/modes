#!/bin/zsh
set -e
INXML=prod_save/normal/2024-08-29_prod_save.xml
OUTFULLXML=prod_update/normal/2024-08-29_cutting_size.xml
OUTDELTAXML=prod_delta/normal/2024-08-29_cutting_size.xml
INCSV=data/cuttings/cutting_sizes.csv
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
cat >tmp/${SCRIPT}.yml <<EOF
cmd: column
xpath: ./Description/Measurement/Reading
title: H x W
EOF
python src/update_from_csv.py $INXML $OUTDELTAXML -c tmp/${SCRIPT}.yml -m $INCSV -v 1
python src/update_from_csv.py $INXML $OUTFULLXML -c tmp/${SCRIPT}.yml -m $INCSV -a -v 2
