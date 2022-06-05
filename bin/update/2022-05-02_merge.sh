python src/csv2xml.py -c src/cfg/y006_accession.yml --template_dir etc/templates/normal -i data/acquisitions/accessions_2021-08-03_2022-05-02.csv -o tmp/normal/acc3.xml
python src/merge_xml.py prod_update/normal/2022-04-27_jb366.xml tmp/normal/acc3.xml prod_update/normal/2022-05-02_merge.xml
#
# The new format after modifying template directory handling is:
python src/csv2xml.py -c src/cfg/y006_accession.yml -i data/acquisitions/accessions_2021-08-03_2022-05-02.csv -o tmp/normal/acc4.xml
#
# Also, the config was updated to include the template_dir statement so that the template is specified in the config
# rather than on the command line.

