# EXSTR is processed by get_exhibition_dict() which is called by exhibition.py
# to create a dictionary for reference when updating the Modes XML file.
#
# The Place field is optional and defaults to the HRM.
#
# NOTE: The dates must be in ISO yyyy-mm-dd format.
#
# Old name:
# 18,2003-11-03,2004-01-18,Dulwich,Dulwich Picture Gallery

from collections import namedtuple
import csv
from datetime import date

ExhibitionTuple = namedtuple('ExhibitionTuple',
                             'DateBegin DateEnd ExhibitionName Place')

EXSTR = '''Serial,DateBegin,DateEnd,ExhibitionName,Place
1,2016-10-15,2017-01-08,Heath Robinson at War
2,2017-01-21,2017-03-26,The Brothers Robinson
3,2017-04-01,2017-06-11,Edward Ardizzone’s Illustrations
4,2017-06-17,2017-09-03,Rejuvenated Junk
5,2017-09-09,2017-11-26,Visualizing the Water Babies
6,2017-12-02,2018-02-18,Heath Robinson’s World of Advertising
7,2018-02-24,2018-05-20,Neo-Romantic Book Illustrations in Britain 1943-1955
8,2018-05-26,2018-08-19,"A Curious Turn: Moving, Mechanical Sculpture"
9,2018-08-25,2018-11-18,Peter Pan and Other Lost Children
10,2018-11-01,2018-11-18,Special Mini Exhibition in Honour of WWI Centenary
11,2018-11-24,2019-02-24,Heath Robinson’s Home Life
12,2019-03-02,2019-05-19,The Beardsley Generation
13,2019-05-25,2019-09-01,Tim Lewis: Post Nature
14,2019-09-07,2019-11-24,Heath Robinson Watercolours
15,2019-11-30,2020-02-23,Fairies in Illustration
16,2020-02-29,2021-03-20,Charles Keeping Illustrations
17,2018-01-20,2018-04-15,Heath Robinson: Dreams and Machines,Mottisfont Abbey
18,2003-11-03,2004-01-18,The Art of William Heath Robinson,Dulwich Picture Gallery
19,2019-04-01,2019-06-30,Heath Robinson Runs Again,NMOC
20,2021-07-03,2021-08-28,"Heath Robinson Exhibition, Haslemere",Haslemere Museum
21,2018-11-07,2019-03-24,Home Futures,Design Museum
22,2017-03-04,2017-05-21,Wonder and Whimsy: The Illustrations of W. Heath Robinson,Delaware Art Museum
23,2016-03-08,2016-06-03,William Heath Robinson’s Life of Line,"Library Print Room, Royal Academy of Arts"
24,2022-01-15,2022-05-15,Heath Robinson’s Children’s Stories
25,2021-10-27,2022-01-30,The Art of W. Heath Robinson,The Willis Museum
26,2022-05-21,2022-09-04,The Humour of William Heath Robinson
27,2019-03-02,2019-05-27,The Beardsley Generation
28,2021-10-21,2022-04-03,Beano: The Art of Breaking the Rules,Somerset House
29,2022-12-29,2023-03-19,Heath Robinson’s Shakespeare Illustrations
30,2023-03-25,2023-06-18,Hidden Treasures
31,2023-06-12,2023-07-15,Heath Robinson’s Watercolours,Jersey Arts Centre
32,2023-06-24,2023-09-17,Happily Ever After?
33,2023-09-23,2024-01-07,Illustrating the Grotesque
34,2024-01-20,2024-04-14,Heath Robinson at War,Mottisfont Abbey
35,2024-03-30,2024-06-23,Modernist Magazine Illustration
36,1992-02-15,1992-03-20,"The Brothers Robinson:Charles, Thomas Heath and William Heath Robinson",Chris Beatles Gallery
37,2024-01-13,2024-03-24,"Mary V. Wheelhouse: suffragette, illustrator and toymaker"
38,2016-10-01,2017-04-17,Den Store Opfindelses Udstilling,Storm P. Museum
39,2025-02-15,2025-05-10,Ralph Steadman: INKling
40,2025-05-17,2025-07-19,Ways of Seeing
41,2025-05-29,2025-06-04,BBC Antique Road Show,Stephens House & Gardens
'''
# data for testing
'''
999,2022-10-15,2017-01-08,Heath Robinson at War
999,2021-10-15,2022-01-08,Heath Robinson at War
'''


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
        exhib_num = int(row[0])
        if exhib_num in exdic:
            raise ValueError(f"Exhibition number duplicated: {exhib_num}.")
        exdic[exhib_num] = ExhibitionTuple(DateBegin=date.fromisoformat(row[1]),
                                           DateEnd=date.fromisoformat(row[2]),
                                           ExhibitionName=row[3],
                                           Place=row[4] if len(row) >= 5 else 'HRM'
                                           )
        if exdic[int(row[0])].DateBegin > exdic[int(row[0])].DateEnd:
            raise ValueError(f"In exhibition_list.py, Begin Date > End Date: {row}")
    return exdic


def get_inverted_exhibition_dict():
    exhibition_dict = get_exhibition_dict()
    inv_dict = {}
    for key, val in exhibition_dict.items():
        inv_dict[val] = key
    return inv_dict


if __name__ == '__main__':
    print('This module is not executable.')
