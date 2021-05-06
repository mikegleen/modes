"""
    Convert the file names which are like "4. Filming Queen of the Harem .jpg"
    to file names like JB052.jpg using the CSV file that has a mapping of
    Serial # -> Accession #.
"""
import codecs
import csv
import os.path
import re
import shutil

CSVPATH = 'results/csv/hr_at_war_v3mlg.csv'
INCLUDECSVPATH = 'results/csv/include_hr_at_war_v3mlg.csv'
IMGSPATH = '/Volumes/Transcend/Downloads/hrmalt/Heath Robinson at War'

# Folder to contain renamed .jpg files:
ACCESSIONEDPATH = 'results/img/accessioned_hr_at_war'

imgs = os.listdir(IMGSPATH)
imgdict = {}
for filename in imgs:
    m = re.match(r'(\d+)\.', filename)
    if m:
        ix = int(m.group(1))
        imgdict[ix] = filename
    else:
        print(f'skipping {filename}')

includecsvfile = open(INCLUDECSVPATH, 'w')
csvfile = codecs.open(CSVPATH, 'r', 'utf-8-sig')
reader = csv.DictReader(csvfile)
for row in reader:
    serial = int(row['SERIAL'])
    accnum = row['Collection']
    if accnum.lower() == 'loan':
        continue
    newfilename = accnum.upper() + '.jpg'
    source = os.path.join(IMGSPATH, imgdict[serial])
    dest = os.path.join(ACCESSIONEDPATH, newfilename)
    # shutil.copy(source, dest)
    # print(f'{dest=},  {source=}')
    print(accnum, file=includecsvfile)
