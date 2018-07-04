# DO NOT USE - PRODUCES BAD HTML
# ------------------------------
echo Script aborted. Use Microsoft Word and export manually. Sorry.
exit
# One parameter is required, the filename without the leading directory
# name or trailing ".doc". It is expected to be in directory "data" and
# will put its output in results/html and results/csv
#
~/bin/soffice --headless --convert-to html data/$1.doc --outdir results/html
python src/html2csv.py $1.html
