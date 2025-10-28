#!/bin/zsh
#
python src/once/x062_list_all_images.py ~/Pictures/VueScan  tmp/listvue.csv
python src/once/x062_list_all_images.py ..  tmp/listall.csv
python src/once/x063_merge_image_lists.py tmp/listall.csv tmp/listvue.csv tmp/allmergelist.cs
python src/once/x063_merge_image_lists.py tmp/listall.csv tmp/listvue.csv tmp/mergelist.csv -p  # only with duplicates

