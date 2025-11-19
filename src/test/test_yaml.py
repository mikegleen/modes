"""
    Test whether the "Norway problem" is fixed.
"""

from ruamel.yaml import YAML

import csv
import io

data = '''cmd: col
country: no
town: null
city: none
street: false
s2: f
s3: 23
'''
infile = io.StringIO(data)
yaml = YAML()
cfg = [c for c in yaml.load_all(infile)]
print('round-trip\n', cfg)

infile = io.StringIO(data)
yaml = YAML(typ='safe', pure=True)   # default, if not specfied, is 'rt' (round-trip)
cfg = [c for c in yaml.load_all(infile)]
print('safe\n', cfg)

