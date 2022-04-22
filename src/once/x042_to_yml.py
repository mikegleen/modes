"""

"""
from collections import namedtuple
import csv
from datetime import date
import sys
import yaml

from cfg.exhibition_list import EXSTR
from exhibition import ExhibitionTuple


def get_exhibition_dict():
    """
    EXSTR is imported from exhibition_list.py and contains a CSV formatted
    multi-line string. The heading line contains:
        ExNum,DateBegin,DateEnd,ExhibitionName[,Place]

    :return: A dictionary mapping the exhibition number to the Exhibition
             namedtuple.
    """
    exhibition_list = EXSTR.split('\n')
    reader = csv.reader(exhibition_list, delimiter=',')
    next(reader)  # skip heading

    exdic = {}
    for row in reader:
        if not row:
            continue
        exdic[int(row[0])] = ExhibitionTuple(ExNum=row[0],
                                             DateBegin=date.fromisoformat(row[1]),
                                             DateEnd=date.fromisoformat(row[2]),
                                             ExhibitionName=row[3],
                                             Place=row[4] if len(row) >= 5 else 'HRM'
                                             )._asdict()
        if exdic[int(row[0])]["DateBegin"] > exdic[int(row[0])]["DateEnd"]:
            raise ValueError(f"In exhibition_list.py, Begin Date > End Date: {row}")
    return exdic


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    exd = get_exhibition_dict()
    print(exd)
    with open('tmp/toyaml.yml', 'a') as f:
        yaml.dump(exd, f)
