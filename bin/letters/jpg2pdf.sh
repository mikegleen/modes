pushd ..
for subdir in letters/letters_edited/*
# do
#     bn=$(basename $subdir)
#     mkdir -p letters/letters_pdf/$bn
#     python src/web/trans2pdf.py letters/letters_edited/$bn letters/letters_pdf/$bn
# done
filterfile=../letters/2023-09-12_letters.xlsx
python src/web/merge_letters.py ../letters/letters_pdf  ../letters/letters_merged  -f $filterfile
