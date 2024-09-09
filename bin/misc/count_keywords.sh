cat >tmp/count_keywords.yml <<EOF
cmd: count
xpath: ./Description/Material[Part="medium"]/Keyword
EOF
python src/xml2csv.py /Users/mlg/pyprj/hrm/modes/prod_update/normal/2024-09-01a_part.xml tmp/count_keywords.csv -c tmp/count_keywords.yml
