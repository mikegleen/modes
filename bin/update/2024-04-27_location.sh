#!/bin/zsh
set -e
INXML=2024-04-27_manual.xml
OUTXML=2024-04-27d_mottisfont.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
#
echo ----------------------------------------------------
# The input file was created manually to remove Mottisfont from JB145
echo Step 0. Add JB315 to the Mottisfont exhibition.
echo ----------------------------------------------------
#
python src/exhibition.py prod_update/normal/$INXML \
                        -o results/xml/normal/2024-04-27a_JB315.xml -e 34 -j JB315 -a
python src/location.py update -i results/xml/normal/2024-04-27a_JB315.xml -o results/xml/normal/2024-04-27b_JB315loc.xml -a \
                        -j JB315 -c -l 'Mottisfont Abbey' -d 2.2.2024
#
echo Step 0.5 Add four objects to the watercolours exhibition that have already had their
echo          location updated.
python src/exhibition.py results/xml/normal/2024-04-27b_JB315loc.xml \
                        -o results/xml/normal/2024-04-27c_watercolours.xml -e 14 -j "LDHRM.2019.13&16&17&23" -a
#
echo ----------------------------------------------------
echo Step 1. Relocate pictures in frames to smaller shelf
echo ----------------------------------------------------
#
cat >tmp/location.csv <<EOF
LDHRM:2021.2
LDHRM:2021.3
LDHRM:2021.5
LDHRM:2021.8-12
LDHRM:2021.17
EOF
python src/location.py update -i results/xml/normal/2024-04-27c_watercolours.xml -o results/xml/normal/step12024-04-27d_r4_to_r5.xml \
                    -l R5 -a -n -c -m tmp/location.csv \
                    -r 'better fitting shelf'
#
echo ----------------------------------------------------
echo Step 2. Change the normal location of a few pictures
echo ----------------------------------------------------
#
python src/location.py update -i results/xml/normal/step12024-04-27d_r4_to_r5.xml -o results/xml/normal/step2.xml \
                       -j SH34,JB392a -a -n -l S19 \
                       -r 'S17 was too full'
#
echo ----------------------------------------------------
echo Step 3. Return Mottisfont to the store
echo ----------------------------------------------------
#
cat >tmp/ifexhib.yml <<EOF
cmd: ifexhib
value: 34
---
cmd: column
xpath: ./ObjectLocation[@elementtype="normal location"]/Location
title: Normal Loc
---
EOF
python src/xml2csv.py results/xml/normal/step1.xml tmp/step3.csv -c tmp/ifexhib.yml
python src/location.py update -i results/xml/normal/step2.xml -o prod_update/normal/$OUTXML \
                        -a -c -m tmp/step3.csv -v 1
