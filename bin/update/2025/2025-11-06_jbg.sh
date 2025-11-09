#!/bin/zsh
#
#
set -e
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
NEWXML=${SCRIPT}_pretty.xml
INXML=$(python src/utl/x066_latest.py -i prod_update/pretty --newxml $NEWXML)
echo INXML: $INXML
OUTXML=prod_update/pretty/${NEWXML}
DELTAXML=prod_delta/pretty/${SCRIPT}_delta_pretty.xml
echo OUTXML: $OUTXML
cat > tmp/sed.sed <<EOF
s;<Location>JBG</Location>;<Location>Joan Brinsmead Gallery</Location>;
EOF
sed -f tmp/sed.sed $INXML >$OUTXML
python src/xmldiff.py $INXML $OUTXML -o $DELTAXML --outorig tmp/orig.xml
bin/syncupdate.sh
bin/syncdelta.sh
