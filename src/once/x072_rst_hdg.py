"""
    Convert configuration.rst from using bullet points for commands and statements
    to making each one a separate paragraph with a heading and
"""
import re
import sys

infile = open(sys.argv[1])
outfile = open(sys.argv[2], 'w')


def state0():
    outfile.write(line)
    if line.startswith('Statements'):
        return 1
    return 0


def state1():
    m = re.match(r'-  \*\*([^*]+)', line)
    if m is None:
        outfile.write(line)
        return 1
    hdg = m[1]  # heading
    ref = hdg
    if hdg.startswith('cmd: '):
        ref = hdg.replace('cmd: ', r'cmd\:_')
        hdg = hdg.removeprefix('cmd: ')
    suffix = '' if hdg.endswith(':') else ':'
    outfile.write(f'\n.. _{ref}{suffix}\n')
    outfile.write(f'\n{hdg}\n')
    outfile.write(f"{'-' * len(hdg)}\n")
    return 1


machine = {0: state0,
           1: state1,
           }
state = 0
for line in infile:
    state = machine[state]()
