"""
    Copied from X023:
    Convert the file names which are like "4. Filming Queen of the Harem .jpg"
    to file names like JB052.jpg using the CSV file that has a mapping of
    Serial # -> Accession #.


"""
import codecs
import csv
import os.path
import re
import shutil

from utl.list_objects import list_objects
from utl.normalize import normalize_id, denormalize_id

CSVPATH = 'results/csv/exhibitions/children_4.csv'
IMGSPATH = '/Users/mlg/T/Old Downloads/hrmalt/Childrens Stories/Heath Robinson_s Children_s Stories'

# Modes file to get legal accession numbers
XMLPATH = 'prod_update/normal/2022-01-15_exhibition.xml'

# Output:
# The "includecsv" file lists JPG files selected
INCLUDECSVPATH = 'results/csv/exhibitions/include_children.csv'
# Folder to contain renamed .jpg files:
ACCESSIONEDPATH = 'results/img/accessioned_children'

objects = list_objects(XMLPATH)
imgs = os.listdir(IMGSPATH)

includecsvfile = open(INCLUDECSVPATH, 'w')
csvfile = codecs.open(CSVPATH, 'r', 'utf-8-sig')
reader = csv.DictReader(csvfile)
objset = set(n.normalized for n in objects)

cat2accn = {}
for row in reader:
    cat = row['Cat'].strip()  # catalogue number
    if not cat:
        continue
    ac = row['Accn. No.']
    try:
        accnum = normalize_id(ac.strip())
    except ValueError:
        print(f'bad accnum: skipping {cat}: "{ac}"')
        continue
    if accnum not in objset:
        print(f'skipping {cat}: "{accnum}"')
        continue
    cat2accn[cat] = accnum

for filename in imgs:
    m = re.match(r'(\d+\w?)\.', filename)
    if m:
        cat = m.group(1)
    else:
        print(f'skipping image: {filename}')
        continue
    try:
        accnum = cat2accn[cat]
    except KeyError:
        continue
    newfilename = denormalize_id(accnum) + '.jpg'
    source = os.path.join(IMGSPATH, filename)
    dest = os.path.join(ACCESSIONEDPATH, newfilename)
    shutil.copy(source, dest)
    print(f'{dest=},  {source=}')
    print(accnum, file=includecsvfile)
