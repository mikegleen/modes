"""
Convert the item number is the first column to a proper accession number,
taking the prefix from the filename. So, in JB1210.csv, item number 1 becomes
JB1210.1 and so on.

Also write to a separate file the accession number of the parent object.
"""
import codecs
import os

indir = '/Users/mlg/pyprj/hrm/letters/letters_index_csv'
outcsvname = '/Users/mlg/pyprj/hrm/letters/letters_index_reformed.csv'
outaccname = '/Users/mlg/pyprj/hrm/letters/letters_accession_numbers.csv'
# outcsvname = 'tmp/letters_index_reformed.csv'

outcsv = codecs.open(outcsvname, 'w', 'utf-8-sig')
outacc = codecs.open(outaccname, 'w', 'utf-8-sig')
written = False

for filename in sorted(os.listdir(indir)):
    prefix, suffix = os.path.splitext(filename)
    print(f'Processing {prefix}{suffix}')
    if not filename.endswith('.csv'):
        print('Skipping', filename)
        continue
    print(prefix, file=outacc)
    incsvpath = os.path.join(indir, filename)
    incsv = codecs.open(incsvpath, 'r', 'utf-8-sig')
    header = next(incsv)
    if not written:
        outcsv.write(header)
        written = True
    for row in incsv:
        row = f'{prefix}.{row}'
        # discard empty rows
        row = row.rstrip(',\n')
        if ',' not in row:
            continue
        print(row, file=outcsv)
    incsv.close()
