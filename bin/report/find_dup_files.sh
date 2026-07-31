#!/bin/zsh
#
# python src/utl/x062_list_all_images.py .. ~/Pictures/VueScan  -o tmp/listall.csv
# python src/utl/x062_list_all_images.py .. ~/Pictures/VueScan  -o tmp/listdup.csv -p
# python src/utl/x062_list_all_images.py .. ~/Pictures/VueScan  -o tmp/listnodup.csv -q
# python src/utl/x062_list_all_images.py ../scans/box\ scans\ edited/g1 ../scans/box\ scans\ edited/g1-2  -o tmp/listg1.csv  --nokeydir results/img
# python src/utl/x062_list_all_images.py .. ~/Pictures/VueScan  -o tmp/listinacc.csv  --nokeydir results/img
INXML=`python src/utl/x066_latest.py -i prod_update/normal`
CANDIDATE='"../collection/candidates_large"'
CANDIDATE="../scans/box scans edited"
CANDIDATE="/Users/mlg/Pictures/VueScan/hrmbox"
python src/web/harvest_new.py --candidate $CANDIDATE \
                              --done      results/img \
                              --modes     $INXML \
                              --staging   ../collection/staging \
                              --verbose 1
                              # --dryrun
