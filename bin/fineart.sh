 python src/xml2csv.py /Users/mlg/pyprj/hrm/modes/results/xml/pretty/2021-02-09_aspect_pretty.xml results/csv/from_fine_art.csv -c src/cfg/select_fine_art.yml -v 1 --heading
 python src/csv2xml.py results/csv/from_fine_art.csv -c src/cfg/merge_fine_art.yml etc/templates/Original_Artwork.xml results/xml/fine_art_as_orig_artwork.xml

