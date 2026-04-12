#!/bin/zsh
#
#   Remove all files in prod_save/normal and .../pretty that do not have "sorted" in the filename.
#
pushd /Users/mlg/pyprj/hrm/modes
ls prod_save/normal |grep -v sorted|xargs -I{} rm prod_save/normal/{}
ls prod_save/pretty |grep -v sorted|xargs -I{} rm prod_save/pretty/{}
