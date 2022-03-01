"""
The input file olddulwich.csv was produced by xml2csv.py with cfg
production_date.yml.
"""
import codecs
import csv
masterfilename = 'data/exhibitions/2022-02-14_update_from_dulwich_R10.csv'
detailfilename = 'tmp/olddulwich.csv'
outmasterfilename = 'results/csv/2022-03-01_dulwich_comp.csv'

inmaster = codecs.open(masterfilename, 'r', 'utf-8-sig')
indetail = codecs.open(detailfilename, 'r', 'utf-8-sig')
outmaster = codecs.open(outmasterfilename, 'w', 'utf-8-sig')

detail = {}
for row in csv.reader(indetail):
    detail[row[0].upper()] = row

outwriter = csv.writer(outmaster)
for row in csv.reader(inmaster):
    key = row[0].upper()
    if not key:
        outwriter.writerow(row)
        continue
    if key not in detail:
        print(f'key not found: {row}')
        outwriter.writerow(row)
        continue
    oldrow = detail[key]
    row[4] = oldrow[1]
    row[6] = oldrow[2]
    row[9] = oldrow[3]
    outwriter.writerow(row)
