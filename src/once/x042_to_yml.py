"""

"""
import csv
from datetime import date
import sys
# import yaml
from ruamel.yaml import YAML

from utl.exhibition_list import get_exhibition_dict, get_exhibition_set
from exhibition import ExhibitionTuple

yaml = YAML(typ='safe')


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    exd = get_exhibition_dict()
    exs = get_exhibition_set(exd)
    # print(exd)
    print(f'{type(exs)=}')
    exs = set([tuple(x) for x in exs])
    with open('tmp/toyaml.yml', 'a') as f:
        yaml.dump(exs, f)
