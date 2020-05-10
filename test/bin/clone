if [[ $# -ne 3 ]]; then
	echo "Must have three parameters, old test group, new test group, and test name."
	exit 2
fi
mkdir -p data/test/$2/csv
mkdir -p data/test/$2/xml
mkdir -p data/test/$2/yml
sed s/$1/$2/ bin/test/$1 >bin/test/$2
test -f data/test/$1/csv/$3.csv && cp data/test/$1/csv/$3.csv data/test/$2/csv/$3.csv
test -f data/test/$1/xml/$3.xml && cp data/test/$1/xml/$3.xml data/test/$2/xml/$3.xml
test -f data/test/$1/yml/$3.yml && cp data/test/$1/yml/$3.yml data/test/$2/yml/$3.yml
