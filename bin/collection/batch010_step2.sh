# From the staging directory, create a list of the accession numbers
python src/web/list_imgs.py ../collection/staging  -o tmp/imglist.csv
#
# Shrink the images in the staging directory and put them in the aawebimgs
# directory from which they will be ftp'd to the WordPress host.
#
python src/web/shrinkjpg.py ../collection/staging ../collection/aawebimgs/batch010
