#!/bin/zsh
#
# This is a log of actions taken. Do not execute!
#
exit
cat >tmp/cfg.yml <<EOF
cmd: column
xpath: ./Identification/Title
---
cmd: column
xpath: ./Identification/BriefDescription
---
cmd: column
xpath: ./Production/SummaryText
---
EOF
# python src/update_from_csv.py prod_update/normal/2022-06-15_merge_2022.xml prod_update/normal/2022-06-29_unpub_title.xml -c tmp/cfg.yml -e -a -m data/csv/2022-06-29_unpub_title.csv
# python src/xml2csv.py prod_update/normal/2022-06-29_unpub_title.xml tmp/unpub_brief_des.csv -c tmp/iftitle.yml --heading
#
# Manually copy tmp/unpub_brief_des.csv to data/csv/2022-06-29_unpub_brief_des.csv and edit.
#
python src/update_from_csv.py prod_update/normal/2022-06-29_unpub_title.xml prod_update/normal/2022-06-29_unpub_brief_des.xml -m data/csv/2022-06-29_unpub_brief_des.csv -c tmp/cfg.yml -e -a

sed 's/Framed R/R/' prod_update/pretty/2022-06-29_unpub_brief_des_pretty.xml >prod_update/pretty/2022-06-30_unframed_pretty.xml
sed 's/framed R/R/' prod_update/pretty/2022-06-30_unframed_pretty.xml >prod_update/pretty/2022-06-30_unframed2_pretty.xml
sed 's/FRAMED R/R/' prod_update/pretty/2022-06-30_unframed2_pretty.xml >prod_update/pretty/2022-06-30_unframed3_pretty.xml
sed 's/Framed-R/R/' prod_update/pretty/2022-06-30_unframed3_pretty.xml >prod_update/pretty/2022-06-30_unframed4_pretty.xml
bin/normal prod_update/pretty/2022-06-30_unframed4_pretty.xml
