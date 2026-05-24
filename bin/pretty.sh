#!/bin/zsh
set -e
if [[ "$CONDA_DEFAULT_ENV" != $MODES_ENV ]] ; then
    echo Activating $MODES_ENV...
    eval "$(conda shell.bash hook)"
    conda activate $MODES_ENV
fi
pushd ~/pyprj/hrm/modes
INXML=`basename $1`
echo INXML = $INXML
INDIR=`dirname $1`
echo INDIR = $INDIR
BASE=`basename $INDIR`
if [[ "$BASE" != "normal" ]]; then
    echo XML file must be in folder named "normal". Exiting
    exit 1
fi
OUTDIR=`dirname $INDIR`/pretty
echo OUTDIR = $OUTDIR
BASENAME=`python3 -c "print('$INXML'.split('.')[0])"`
BASENAME=$(basename -- ${INXML%.*})
PRETTYPATH="$OUTDIR/${BASENAME}_pretty.xml"
echo Creating: $PRETTYPATH
python src/normalize_xml.py -p -n $1 $PRETTYPATH
