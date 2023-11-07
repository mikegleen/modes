#!/bin/zsh
set -e
INCSV=../letters/etc/2023-10-31_letters.xlsx
OUTXML=2023-11-02_letters.xml
cat >tmp/update.yml <<EOF
cmd: global
template_title: Type
template_dir: /Users/mlg/pyprj/hrm/modes/etc/templates/normal
templates:
  cutting: 2023-08-28_cutting_template.xml
  ephemera: 2023-08-29_ephemera_template.xml
  letter: 2023-10-09_letters_template.xml
---
cmd: column
xpath: ./Description/Aspect[Keyword="pages"]/Reading
title: Pages
---
cmd: column
xpath: ./Production/Date/DateBegin
parent_path: ./Production/Date
date:
title: Date
---
cmd: column
xpath: ./Production/Date/Accuracy
parent_path: ./Production/Date
---
cmd: column
xpath: ./Production/Person[Role="sender"]/PersonName
title: Person From
---
cmd: column
xpath: ./Production/Organisation[Role="sender"]/OrganisationName
title: Org From
---
cmd: column
xpath: ./Production/Person[Role="recipient"]/PersonName
title: Person To
---
cmd: column
xpath: ./Production/Organisation[Role="recipient"]/OrganisationName
title: Org To
---
cmd: column
xpath: ./Production/Organisation[Role="publication name"]/OrganisationName
title: Publ Name
---
cmd: column
xpath: ./Identification/Title
title: Title
---
cmd: column
xpath: ./Production/Person[Role="author"]/PersonName
title: Author
---
cmd: column
xpath: ./Identification/BriefDescription
title: Description
---
cmd: column
xpath: ./ObjectLocation[@elementtype="current location"]/Location
xpath2: ./ObjectLocation[@elementtype="normal location"]/Location
title: Location
---
cmd: constant
xpath: ./ObjectLocation[@elementtype="current location"]/Date/DateBegin
title: Location Date
value: 13.9.2023
---
EOF
python src/csv2xml.py -o prod_make/normal/$OUTXML \
                      -c tmp/update.yml -i $INCSV -v 1 --nostrict
bin/syncmake.sh
