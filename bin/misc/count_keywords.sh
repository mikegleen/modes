cat >tmp/count_keywords.yml <<EOF
cmd: count
xpath: ./Description/Material[Part="medium"]/Keyword
EOF
python src/xml2csv.py /Users/mlg/pyprj/hrm/modes/prod_update/pretty/2023-04-18_batch020_pretty.xml tmp/count_keywords.csv -c tmp/count_keywords.yml
