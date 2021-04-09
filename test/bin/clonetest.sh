if [[ $# -ne 3 ]]; then
	echo "Must have three parameters, test group, old test name, and new test name."
	exit 2
fi
cp test/$1/csv/$2.csv test/$1/csv/$3.csv
cp test/$1/xml/$2.xml test/$1/xml/$3.xml
cp test/$1/yml/$2.yml test/$1/yml/$3.yml
