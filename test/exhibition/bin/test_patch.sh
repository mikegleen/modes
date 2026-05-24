#!/bin/zsh
#
# The input file has been modified to insert the wrong start date for one of the exhibitions.
# The exhibitions have been re-arranged to be out of order (most recent first).
#
root=~/pyprj/hrm/modes
tfile=test_patch2.xml
tpath=test/exhibition
verbose=2
#
pushd $tpath
touch results/normal
rm -f results/normal/*
python $root/src/exhibition.py xml/normal/$tfile \
        --outfile results/normal/$tfile \
        --exhibition 18 \
        --patch -v 1
# Create pretty for inspection.
python $root/src/sync_xml.py xml $*
python $root/src/sync_xml.py results $*
python $root/src/sync_xml.py baseline $*
source ../bin/validate.sh $? normal/$tfile -v $verbose
