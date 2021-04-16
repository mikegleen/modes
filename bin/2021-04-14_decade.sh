python src/xml2csv.py results/xml/pretty/2021-04-14_move_pretty.xml results/csv/2021-04-14_website.csv -c src/cfg/website.yml --include data/2021-03-26_website.csv --include_skip 0 --heading -v 2 >results/reports/2021-04-14_website.txt
python src/decade_csv.py results/csv/2021-04-14_website.csv results/csv/2021-04-14_decade.csv
