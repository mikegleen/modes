#!/bin/zsh
set -e
INXML=2024-04-27d_mottisfont.xml
OUTXML=2024-06-01_measure.xml
INXML=prod_update/normal/$INXML
OUTDELTA=prod_delta/normal/$OUTXML
OUTFULL=prod_update/normal/$OUTXML
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('/')[-1].split('.')[0])")
# echo SCRIPT: $SCRIPT
green () {
    print -P "%F{green}$*%f"
}
yellow () {
    print -P "%F{yellow}$*%f"
}
#
# Update deferred:
# 2023.10,266x191,measured in frame
# 2023.11,175x243,measured in frame
# 2023.12,143x173,measured in frame
# 2023.13,153x88,measured in frame
# 2023.14,195x336,measured in frame
# 2023.15,343x173,measured in frame
# 2023.16,297x240,measured in frame
# 2023.17,440x272,measured in frame
# 2023.18,352x250,measured in frame
# 2023.20,218x143,measured in frame
# 2023.21,256x142,measured in frame
# 2023.22,246x184,measured in frame
#
cat >tmp/${SCRIPT}.csv <<EOF
Serial,HxW,Note
2018.25,270x190,
2021.26,160x195,
2022.28,75x108,
2022.34,520x405,
2022.8,200x340,
jb146,110x550,
jb636,313x260,measured in frame
jb705,125x190,
sh19,373x246,measured in frame
sh22,457x366,measured in frame
sh26,440x348,
sh29,451x334,measured in frame
sh30,384x304,measured in frame
sh43,415x315,
sh50,365x264,measured in frame
sh56,390x275,
sh58,380x295,
sh65,425x345,
sh68,125x580,
sh8,385x295,
sh9,430x285,
EOF
cat >tmp/${SCRIPT}.yml <<EOF
cmd: column
xpath: ./Description/Measurement[Part="Image"]/Reading
title: HxW
---
cmd: column
xpath: ./Description/Measurement[Part="Image"]/Note
parent_path:  ./Description/Measurement[Part="Image"]
EOF
python src/update_from_csv.py $INXML $OUTDELTA -c tmp/${SCRIPT}.yml -m tmp/${SCRIPT}.csv -v 1
python src/update_from_csv.py $INXML $OUTFULL -c tmp/${SCRIPT}.yml -m tmp/${SCRIPT}.csv -a -v 1
