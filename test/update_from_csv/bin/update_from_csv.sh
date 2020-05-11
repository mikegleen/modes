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
app=`basename $0|cut -d. -f1`
tpath=test/$app
tst=$1  # get the test name
shift  # now $* contains the parameters to pass to the app
python src/$app.py $tpath/xml/$tst.xml $tpath/results/$tst.xml -c $tpath/yml/$tst.yml -m  $tpath/csv/$tst.csv $*
diff -q $tpath/baseline/$tst.xml $tpath/results/$tst.xml &>/dev/null
if [ $? ]  # if bad compare
then
# display the names of the offending files
diff -q $tpath/baseline/$tst.xml $tpath/results/$tst.xml
fi
