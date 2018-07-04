# -*- coding: utf-8 -*-
"""
    Read a file containing records of:

    index.imageheight.imagewidth[.frameheight.framewidth]

    The index can be of the form JB001 or sh3 or simply a number. If it is a
    number, use the most recent alphabetic preamble.

    Output: index,"height x width",["frameheight x framewidth"]

"""
import re
import sys


def main(r):
    global id_preamble
    row = r.split('.')
    m = re.match(r'([a-zA-Z]*)(\d+)', row[0])
    if not m:
        print(f'match failed: "{r}"')
        return
    if m.group(1):
        id_preamble = m.group(1).upper()  # JB...
    index = id_preamble + m.group(2)  # JB123
    img_reading = f'{row[1]} x {row[2]}'
    if len(row) > 3:
        frame_reading = f'{row[3]} x {row[4]}'
    else:
        frame_reading = ''
    print(f'{index},{img_reading},{frame_reading}', file=outfile)


if __name__ == '__main__':
    if sys.version_info.major < 3:
        raise ImportError('requires Python 3')
    id_preamble = ''
    infile = open(sys.argv[1])
    outfile = open(sys.argv[2], 'w')
    for line in infile:
        main(line.strip())
