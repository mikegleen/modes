#!/bin/zsh
cat >tmp/make2.csv <<END
Serial
2099.1-9999
END
cat >tmp/make.yml <<END
column: title
xpath: ./Identification/Title
END
python src/csv2xml.py --incsvfile tmp/make.csv --outfile tmp/out.csv --cfgfile tmp/make.yml --template templates/normal/Original_Artwork_template.xml

