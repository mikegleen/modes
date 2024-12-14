pushd doc
touch $1
echo file: $1
make html|grep ERROR
