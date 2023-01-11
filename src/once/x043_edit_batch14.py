"""
The input file olddulwich.csv was produced by xml2csv.py with cfg
production_date.yml.
"""
import codecs
import csv
import re
from utl.excel_cols import col2num
infilename = '../collection/etc/batch014/batch014_step1.csv'
outfilename = '../collection/etc/batch014/batch014_step1_edited.csv'


inmaster = codecs.open(infilename, 'r', 'utf-8-sig')
outmaster = codecs.open(outfilename, 'w', 'utf-8-sig')

outwriter = csv.writer(outmaster)
for row in csv.reader(inmaster):
    for col in (col2num(x) for x in 'BLM'):
        row[col] = re.sub(r'[bB][Kk](.*?)\s?ch(\d+)', r'Book \1, Chapter \2', row[col])
        row[col] = re.sub(r', \d{4}$', '', row[col])
    outwriter.writerow(row)
