#!/bin/zsh
#
#
#
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
INXML=$(python src/utl/x066_latest.py -i prod_save/pretty)
echo INXML: $INXML
OUTXML=prod_update/pretty/${SCRIPT}_pretty.xml
echo OUTXML: $OUTXML
#
cat > tmp/sed.sed <<EOF
s;<PersonName>Robinson, William Heath</PersonName>;<PersonName>Heath Robinson, William</PersonName>;
s;<PersonName>WHR</PersonName>;<PersonName>Heath Robinson, William</PersonName>;
s;<PersonName>Robinson, W Heath</PersonName>;<PersonName>Heath Robinson, William</PersonName>;
s;<PersonName>Robinson, Thomas</PersonName>;<PersonName>Heath Robinson, Thomas</PersonName>;
s;<PersonName>Robinson, W H</PersonName>;<PersonName>Heath Robinson, William</PersonName>;
EOF
sed -f tmp/sed.sed $INXML >$OUTXML
bin/syncupdate.sh
