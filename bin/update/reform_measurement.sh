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
# in the format <height> x <width> mm. For decorative art make it h x w x d.
# There are no cases where the fields are populated so we don't have to worry
# about the Reading field.
#
goawk -i 'csv header'  \
'BEGIN{print "Serial,Dimension,Reading"
       OUTPUTMODE = "csv"}
       { if (@"type" == "decorative art")
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
xpath: ./Description/Measurement[3]
parent_path: ./Description
title: height
---
cmd: delete
xpath: ./Description/Measurement[2]
parent_path: ./Description
title: width
---
cmd: delete
xpath: ./Description/Measurement[1]
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
#
# We've deleted all of the Measurement element groups and created a single
# Measurement of H x W or H x W x D. We now must add an Aspect "# of pages" to
# the ephemera objects.
#
goawk -i 'csv header'  \
'BEGIN{print "Serial"}
       @"Dimension3" == "count"{print @"Serial"}' tmp/hxw.csv >tmp/hxw5.csv
#
cat >tmp/cfg2.yml <<EOF
cmd: constant
xpath: ./Description/Aspect
parent_path: ./Description
insert_after: Measurement
value: number of pages
---
cmd: constant
xpath: ./Description/Aspect/Reading
parent_path: ./Description/Aspect
value:
EOF
python src/update_from_csv.py prod_update/normal/2022-11-05_measurement_hxw.xml \
                              prod_update/normal/2022-11-06_aspect.xml \
                              -c tmp/cfg2.yml \
                              -m tmp/hxw5.csv \
                              -a -e -v 3
