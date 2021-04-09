CSVDIR=results/csv/exhibitions
XMLDIR=results/xml
python src/exhibition.py -a --col_acc 5 --col_cat 0 --exhibition 6  --skiprows 0 --mapfile $CSVDIR/advertising.csv  $XMLDIR/2021-02-14_dev_save.xml $XMLDIR/2021-03-03_adv.xml
python src/exhibition.py -a --col_acc 5 --col_cat 0 --exhibition 2  --skiprows 0 --mapfile $CSVDIR/brothers.csv     $XMLDIR/2021-03-03_adv.xml $XMLDIR/2021-03-03_bro.xml
python src/exhibition.py -a --col_acc 5 --col_cat 0 --exhibition 11 --skiprows 0 --mapfile $CSVDIR/home_life.csv    $XMLDIR/2021-03-03_bro.xml $XMLDIR/2021-03-03_hom.xml
python src/exhibition.py -a --col_acc 1 --col_cat 0 --exhibition 14 --skiprows 1 --mapfile $CSVDIR/watercolours.csv $XMLDIR/2021-03-03_hom.xml $XMLDIR/2021-03-03_wat.xml
python src/exhibition.py -a --col_acc 1 --col_cat 2 --exhibition 18 --skiprows 1 --mapfile $CSVDIR/dulwich2.csv     $XMLDIR/2021-03-03_wat.xml $XMLDIR/2021-03-03_exhib.xml
python src/exhibition.py -a --col_acc 3  --exhibition 17 --skiprows 3 --mapfile $CSVDIR/mottisfont.csv     $XMLDIR/2021-03-03_exhib.xml $XMLDIR/2021-03-05_exhib.xml
python src/exhibition.py -a --col_acc 1 --col_cat 0  --exhibition 15 --skiprows 0 --mapfile $CSVDIR/fairies.csv $XMLDIR/2021-03-05_exhib.xml $XMLDIR/2021-03-05a_exhib.xml
