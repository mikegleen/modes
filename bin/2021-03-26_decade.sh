python src/xml2csv.py results/xml/pretty/2021-04-07_prod_dates_pretty.xml results/csv/2021-04-07_website.csv -c src/cfg/website.yml --include data/2021-03-26_website.csv --include_skip 0 --heading -v 2 >results/reports/2021-04-07_website.txt
python src/decade_csv.py results/csv/2021-04-07_website.csv results/csv/2021-04-07_decade.csv
