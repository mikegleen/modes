#!/bin/zsh
#
#
set -e
# INCLUDE_FILE=tmp/include.csv
INXML=prod_update/normal/2025-08-14a_condition.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
OUTXML=prod_update/normal/$SCRIPT.xml
DELTAXML=prod_delta/normal/${SCRIPT}_delta.xml
MAP_FILE=tmp/include.csv
cat >tmp/include.csv <<EOF
Serial,BriefDescription
JB410,"(a) Think as a duck and be happy – you can't change the weather.(b) You have control of the door to your mind.(c) Without ooperation there is no progress.(d) To correct distribution of the necessaries of life.(e) Was first pictured in his mind.(f)Became conscious of the force of gravity.(These drawings were made to illustrate some short texts written by Chas Ed Potter, who was hoping to syndicate them to American papers on a regular basis under the title ‘Think’. WWII started before the project came to anything.)"
JB411,See JB410 for the description.
EOF
cat >tmp/update.yml <<EOF
column: BriefDescription
xpath: ./Identification/BriefDescription
EOF
python src/update_from_csv.py $INXML --outfile $OUTXML --deltafile $DELTAXML --cfgfile tmp/update.yml --mapfile $MAP_FILE
bin/syncupdate.sh
bin/syncdelta.sh
