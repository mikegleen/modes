"""

"""
import sys

infile = open(sys.argv[1])

state = 0

for line in infile:
    line = line.rstrip()
    if state == 0:
        if '<Object elementtype="books">' in line:
            state = 1
    elif state == 1:
        if '<Number>' in line:
            print(line)
            state = 2
    elif state == 2:
        if '<Content>' in line:
            print(line)
            state = 3
    elif state == 3:
        print(line)
        if '</Content>' in line:
            state = 0
