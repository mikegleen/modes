pushd ..
INDIR=letters/letters_edited
PDFDIR=letters/letters_pdf
MRGDIR=letters/letters_merged
#
INDIR=tmp/test_img
PDFDIR=tmp/test_pdf
MRGDIR=tmp/test_mrg
start=$(date +%s)
for subdir in $INDIR/*
do
    bn=$(basename $subdir)
    mkdir -p $PDFDIR/$bn
    python src/web/img2pdf.py $INDIR/$bn $PDFDIR/$bn
done
end=`date +%s`
echo Execution time was `expr $end - $start` seconds.
# mkdir -p $MRGDIR
# filterfile=../letters/2023-09-12_letters.xlsx
# python src/web/merge_letters.py $PDFDIR  $MRGDIR  -f $filterfile
