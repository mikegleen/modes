set -e
pushd /Users/mlg/pyprj/hrm/modes
SCRIPT="$(basename -- "${0%.*}")"
OUTFILE=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
echo INXML = $INXML
echo OUTXML=$OUTFILE
green () {
    print -P "%F{green}$*%f"
}
yellow () {
    print -P "%F{yellow}$*%f"
}
