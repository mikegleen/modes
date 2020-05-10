"""
Merge the Excel files each of which contains the index of the images for
a set of letters grouped by a single accession number.

The merged file will have an additional column at the left containing the
accession number taken from the individual filenames.
"""
import codecs
import pandas as pd
import os.path

folder = 'data/letters_etc'
mergedfile = 'results/scans/letters_merged2.csv'
csvfile = codecs.open(mergedfile, 'w', 'utf-8-sig')  # insert BOM in file

flist = [f for f in os.listdir(folder)
         if f.endswith('.xlsx') and f != 'template.xlsx'
         and not f.startswith('~')]  # ignore excel temp files
flist = sorted(flist)

template = pd.read_excel(os.path.join(folder, 'template.xlsx'))
outdf = pd.DataFrame(columns=['Accession Number'] + template.columns.tolist())

for fname in flist:
    print(f'{fname=}')
    df = pd.read_excel(os.path.join(folder, fname), dtype=str)
    # Drop if empty except for the serial number.
    df = df.dropna(axis=0, subset=df.columns.tolist()[1:], how='all')
    # Dates from Excel are of the form yyyy-mm-dd hh:mm:ss. Trim off the time.
    df.Date = df.Date.str.slice(stop=10)
    df.insert(0, 'Accession Number', os.path.splitext(fname)[0])
    outdf = outdf.append(df)

outdf.to_csv(csvfile, index=False)
