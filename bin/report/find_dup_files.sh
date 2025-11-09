#!/bin/zsh
#
python src/once/x062_list_all_images.py .. ~/Pictures/VueScan  -o tmp/listall.csv
python src/once/x062_list_all_images.py .. ~/Pictures/VueScan  -o tmp/listnodup.csv -p
