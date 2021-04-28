"""

"""
from datetime import date
import unittest
from utl.normalize import britishdatefrommodes, datefrombritishdate
from utl.normalize import modesdatefrombritishdate, MODESTYPE, BRITISHTYPE


class TestBritishDateFromModes(unittest.TestCase):
    def test_01(self):
        bdate = britishdatefrommodes('12.3.1917')
        self.assertEqual(bdate, '12 Mar 1917')

    def test_06(self):
        bdate = britishdatefrommodes('12.03.1917')
        self.assertEqual(bdate, '12 Mar 1917')


class TestDateFromBritishDate(unittest.TestCase):
    def test_02(self):
        ddate = datefrombritishdate('12 Mar 1917')
        self.assertEqual(ddate, (date(1917, 3, 12), 3, BRITISHTYPE))

    def test_05(self):
        self.assertRaises(ValueError, datefrombritishdate, 'Mar 12 1917')


class TestModesDateFromBritishDate(unittest.TestCase):

    def test_03(self):
        mdate = modesdatefrombritishdate('12 Mar 1917')
        self.assertEqual(mdate, ('12.3.1917', 3, BRITISHTYPE))

    def test_04(self):
        mdate = modesdatefrombritishdate('1917')
        self.assertEqual(mdate, ('1917', 1, MODESTYPE))


if __name__ == '__main__':
    unittest.main()