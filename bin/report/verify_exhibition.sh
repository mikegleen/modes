#!/bin/zsh
set -e
INXML=`python src/utl/x066_latest.py -i prod_update/normal`
echo INXML= $INXML
python src/exhibition.py $INXML --verify
