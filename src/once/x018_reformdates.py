"""
    If a date is in the dd mmm yyyy format, write a record with the serial
    number and the modes format date.

    This program serves two functions. If WRITEALL is True, write all records
    to the output CSV file. If it is False, only write records that have to
    be recoded from "12 May 1909" to "12.5.1909".
"""
import csv
import datetime
import sys

WRITEALL = False

from utl.normalize import datefrommodes, modesdate


def parsedate(indate: str):
    """

    :param indate: the date in Modes format or dd mmm yyyy
    :return: a 3-tuple:
                0. date object or None if cannot parse
                1. boolean: True if good Modes date and False otherwise
                2. int: number of fields in a to-be-reformatted date which is
                        like '12 May 1909'
    """
    indate = indate.strip('.')  # fix one bloody typo
    try:
        d, _ = datefrommodes(indate)
        return d, True, 0
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(indate, '%d %b %Y').date()
        return d, False, 3
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(indate, '%b %Y').date()
        return d, False, 2
    except ValueError:
        pass
    try:
        d = datetime.datetime.strptime(indate, '%Y').date()
        return d, False, 1
    except ValueError:
        pass
    return None, False, 0


def main():
    inf = open(sys.argv[1])
    outf = open(sys.argv[2], 'w')
    reader = csv.reader(inf)
    writer = csv.writer(outf)
    row = next(reader)
    row.append('modesdate')
    row.append('isodate')
    # writer.writerow(row)
    for row in reader:
        indate = row[1]
        d, status, nfields = parsedate(indate)
        print(row, d, status)
        if d:
            if WRITEALL or not status:
                outs = modesdate(d, nfields)
                iso = d.isoformat()
                row.append(outs)
                row.append(iso)
                newrow = [row[0], outs]
                writer.writerow(newrow)
        elif WRITEALL:
            if indate and indate != 'unknown':
                print(f'Cannot parse {row}')
            outs = 'unknown'
            iso = ''
            if indate and indate != 'unknown':
                print(f'{row}')
            row.append(outs)
            row.append(iso)
            writer.writerow(row)


if __name__ == '__main__':
    main()
