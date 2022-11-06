cat >tmp/cfg.yml <<EOF
cmd: ifelt
xpath: ./Description/Measurement[Dimension="height"]/Reading
---
cmd: attrib
xpath: .
attribute: elementtype
title: type
---
cmd: column
xpath: ./Description/Measurement[Dimension="height"]/Reading
title: height
---
cmd: column
xpath: ./Description/Measurement[Dimension="width"]/Reading
title: width
---
cmd: column
xpath: ./Description/Measurement[3]/Dimension
title: Dimension3
---
EOF
python src/xml2csv.py prod_update/pretty/2022-11-01_adopt_pretty.xml tmp/hxw.csv -c tmp/cfg.yml --heading
#
# Extract the two fields "height" and "width" and create a single field
# in the format <height> x <width> mm
#
goawk -i 'csv header'  \
'BEGIN{print "Serial,Dimension,Reading"
       OUTPUTMODE = "csv"}
      @"Dimension3" != "count" { if (@"type" == "decorative art")
          dimension = "height x width x depth"
        else
          dimension = "height x width"
        if (! @"height")
          print @"Serial", dimension
       else
         {
          hxw = sprintf("%s x %s mm", @"height", @"width")
          print  @"Serial", dimension, hxw
         }
      }' tmp/hxw.csv >tmp/hxw4.csv
#
cat >tmp/cfg2.yml <<EOF
cmd: delete
xpath: ./Description/Measurement[Dimension="height"]
parent_path: ./Description
title: height
---
cmd: delete
xpath: ./Description/Measurement[Dimension="width"]
parent_path: ./Description
title: width
---
cmd: delete
xpath: ./Description/Measurement[Dimension="length"]
parent_path: ./Description
title: length
---
cmd: constant
xpath: ./Description/Measurement
parent_path: ./Description
insert_after: SummaryText
value:
---
cmd: column
xpath: ./Description/Measurement/Dimension
parent_path: ./Description/Measurement
---
cmd: column
xpath: ./Description/Measurement/Reading
parent_path: ./Description/Measurement
EOF
python src/update_from_csv.py prod_update/normal/2022-11-01_adopt.xml \
                              prod_update/normal/2022-11-05_measurement_hxw.xml \
                              -c tmp/cfg2.yml \
                              -m tmp/hxw4.csv \
                              -a -e -v 3
