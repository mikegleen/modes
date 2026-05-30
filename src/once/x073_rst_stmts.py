"""
    Convert configuration.rst from using bullet points for commands and statements
    to making each one a separate paragraph with a heading and
"""
import re
import sys

infile = open(sys.argv[1])
outfile = open(sys.argv[2], 'w')

stmt_pat = r'^(.*)\*\*([a-z_]+):\*\*(.*)$'
cmd_pat = r'^(.*)\*\*([a-z_]+)\*\*(.*)$'

for line in infile:
    while m := re.match(stmt_pat, line):
        line = f'{m[1]}:ref:`{m[2]}`{m[3]}'
    while m := re.match(cmd_pat, line):
        line = f'{m[1]}:ref:`cmd_{m[2]}`{m[3]}'
    print(line.rstrip(), file=outfile)
