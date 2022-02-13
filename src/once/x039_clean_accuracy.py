"""

"""
infile = open('prod_update/pretty/2022-02-13_willis_to_hrm_pretty.xml')
outfile = open('prod_update/pretty/2022-02-13_willis_to_hrm2_pretty.xml', 'w')

for row in infile:
    if '<Accuracy />' not in row:
        print(row, file=outfile, end='')
