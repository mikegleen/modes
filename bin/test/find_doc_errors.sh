echo begin find errors
pushd doc
for file in source/*.rst ; do
    touch $file
    echo file: $file
    make html|grep ERROR
done
