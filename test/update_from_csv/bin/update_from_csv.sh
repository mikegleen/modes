# Call this script with the name of the test followed by any parameters to pass to python.
# It assumes that the working directory, modes, has a subdirectory tree as follows:
#
# modes
# ├── test
# │   ├── bin
# │   ├── data
# │   └── update_from_csv
# │       ├── baseline
# │       ├── bin
# │       ├── csv
# │       ├── results
# │       ├── xml
# │       └── yml
#
# If this shell script name is ".../modes/test/xxx/bin/xxx.sh" then app wil be "xxx".
setc -e
app=`basename $0|cut -d. -f1`
tpath=test/$app
tst=$1  # get the test name
shift  # now $* contains the parameters to pass to the app
# The runner uses a leading "-" to indicate that the test is expected to fail.
if [[ "${tst:0:1}" == "-"]]; then
    tst=${tst:1}
fi
python src/$app.py $tpath/xml/$tst.xml $tpath/results/$tst.xml -c $tpath/yml/$tst.yml -m  $tpath/csv/$tst.csv $*
diff -q $tpath/baseline/$tst.xml $tpath/results/$tst.xml
