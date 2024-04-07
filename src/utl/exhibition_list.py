# EXSTR is processed by exhibition.py to create a dictionary for reference
# when updating the Modes XML file.
#
# The Place field is optional and defaults to the HRM.
#
# NOTE: The dates must be in ISO yyyy-mm-dd format.
#
# Old name:
# 18,2003-11-03,2004-01-18,Dulwich,Dulwich Picture Gallery

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
'''
# data for testing
'''
999,2022-10-15,2017-01-08,Heath Robinson at War
999,2021-10-15,2022-01-08,Heath Robinson at War
'''
#
if __name__ == '__main__':
    print('This module is not executable.')
