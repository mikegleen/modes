python src/exhibition.py    prod_update/pretty/2023-03-23b_shakespeare_pretty.xml \
                            tmp/2023-03-24_shakespeare_pretty.xml \
                            -m tmp/shakespeare.csv -s 1 --delete -e 29 -a
#
python src/exhibition.py    tmp/2023-03-24_shakespeare_pretty.xml \
                            prod_update/pretty/2023-03-25_shakespeare_pretty.xml \
                            -e 29 --col_acc b --col_cat a -a -s 1 \
                            -m results/csv/exhibitions/shakespeare.csv
