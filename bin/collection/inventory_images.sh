#!/bin/zsh
pushd ~/pyprj/hrm/modes
python src/once/x062_list_all_images.py ~/Pictures/VueScan  tmp/listvue.csv
python src/once/x062_list_all_images.py ~/pyprj/hrm  tmp/listhrm.csv
python src/once/x063_merge_image_lists.py tmp/listvue.csv tmp/listhrm.csv tmp/allmergelist.csv
