#
# batch010_step1.sh
#
#   hrmbox contains one folder per image. Each folder contains multiple scans
#   each of part of an image. These are manually stitched using Panorama
#   Stitcher creating a complete image. The folder names follow a pattern
#   whereby, e.g., folder JB391 contains image file JB391.jpg.
#
#   Additionally, each box folder may contain compete scans of images.
#
#   hrmbox contained scans from boxes S17, S18, S20, S24.
#
export MODESFILE=prod_update/pretty/2022-06-30_unframed4_pretty.xml
python src/web/harvest_scan.py /Users/mlg/Pictures/VueScan/hrmbox  ../harvested
python src/web/harvest_new.py  -d ../collection/aawebimgs -c ../harvested -s tmp/staging -m $MODESFILE
mv tmp/staging ../collection
#
# Images in ../collection/staging are now manually cropped.
#
