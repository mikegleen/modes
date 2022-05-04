python src/csv2xml.py -c src/cfg/y006_accession.yml --template_dir etc/templates/normal -i data/acquisitions/accessions_2021-08-03_2022-05-02.csv -o tmp/normal/acc3.xml 
python src/merge_xml.py prod_update/normal/2022-04-27_jb366.xml tmp/normal/acc3.xml prod_update/normal/2022-05-02_merge.xml

