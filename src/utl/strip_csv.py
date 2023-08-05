"""
    For each cell in a CSV file, strip leading and trailing whitespace.
"""
import codecs
import csv
import sys


def main():
    incsv = codecs.open(sys.argv[1], 'r', 'utf-8-sig')
    outcsv = codecs.open(sys.argv[2], 'w', 'utf-8-sig')
    outwriter = csv.writer(outcsv)
    for row in csv.reader(incsv):
        for column in range(len(row)):
            row[column] = row[column].strip() if row[column] else row[column]
        outwriter.writerow(row)


if __name__ == '__main__':
    main()
