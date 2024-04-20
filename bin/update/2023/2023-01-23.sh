python src/csv2xml.py -c src/cfg/accession/y013_long_term_loan.yml -i /Users/mlg/pyprj/hrm/modes/data/acquisitions/2023-01-21_L005-10.xlsx  -o tmp/2023-01-23_loan.xml
python src/merge_xml.py /Users/mlg/pyprj/hrm/modes/prod_update/normal/2023-01-11_batch14a.xml tmp/normal/2023-01-23_loan.xml prod_update/normal/2023-01-23_loans.xml
python src/exhibition.py prod_update/normal/2023-01-23_loans.xml prod_update/normal/2023-01-23_shakespeare.xml -a --col_acc b --col_cat a -e 29 -m results/csv/exhibitions/shakespeare.csv
python src/location.py update -i prod_update/normal/2023-01-23_shakespeare.xml -o tmp/normal/2023-01-23_location --col_acc b -l 'Joan Brinsmead Gallery' -m /Users/mlg/pyprj/hrm/modes/results/csv/exhibitions/shakespeare.csv -c -d 20.12.2022

