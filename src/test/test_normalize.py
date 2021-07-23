"""

"""
from datetime import date
import unittest
from utl.normalize import britishdatefrommodes, datefrombritishdate
from utl.normalize import modesdatefrombritishdate, MODESTYPE, BRITISHTYPE
from utl.normalize import normalize_id, denormalize_id


class TestNormalizeId(unittest.TestCase):
    def test_01(self):
        nid = normalize_id('JB001')
        self.assertEqual(nid, 'JB000001')

    def test_01a(self):
        nid = normalize_id('JB1')
        self.assertEqual(nid, 'JB000001')

    def test_01b(self):
        nid = normalize_id('JB1a')
        self.assertEqual(nid, 'JB000001A')

    def test_02(self):
        nid = normalize_id('LDHRM.2018.1')
        self.assertEqual(nid, 'LDHRM.2018.000001')

    def test_03(self):
        nid = normalize_id('LDHRM.2018.1.2')
        self.assertEqual(nid, 'LDHRM.2018.000001.000002')

    def test_04(self):
        with self.assertRaises(AssertionError):
            normalize_id('JB9999999')

    def test_05(self):
        self.assertRaises(AssertionError,
                          normalize_id, 'LDHRM.2018.1.0000002')

    def test_06(self):
        self.assertRaises(ValueError,
                          normalize_id, 'LDHRM.2018.1.')

    def test_07(self):
        self.assertRaises(ValueError,
                          normalize_id, 'LDHRM.2018.1.X')

    def test_08(self):
        self.assertRaises(ValueError,
                          normalize_id, 'LDHRM.2018.')

    def test_09(self):
        self.assertRaises(ValueError,
                          normalize_id, 'LDHRM.2018.x')


class TestDenormalizeId(unittest.TestCase):
    def test_01(self):
        nid = denormalize_id('JB000001')
        self.assertEqual(nid, 'JB001')

    def test_02(self):
        nid = denormalize_id('LDHRM.2018.000001')
        self.assertEqual(nid, 'LDHRM.2018.1')

    def test_03(self):
        nid = denormalize_id('LDHRM.2018.000001.000002')
        self.assertEqual(nid, 'LDHRM.2018.1.2')

    def test_04(self):
        nid = denormalize_id('JB999999999')
        self.assertEqual(nid, 'JB999999999')


class TestBritishDateFromModes(unittest.TestCase):
    def test_01(self):
        bdate = britishdatefrommodes('12.3.1917')
        self.assertEqual(bdate, '12 Mar 1917')

    def test_02(self):
        bdate = britishdatefrommodes('12.03.1917')
        self.assertEqual(bdate, '12 Mar 1917')


class TestDateFromBritishDate(unittest.TestCase):
    def test_01(self):
        ddate = datefrombritishdate('12 Mar 1917')
        self.assertEqual(ddate, (date(1917, 3, 12), 3, BRITISHTYPE))

    def test_02(self):
        self.assertRaises(ValueError, datefrombritishdate, 'Mar 12 1917')


class TestModesDateFromBritishDate(unittest.TestCase):

    def test_01(self):
        mdate = modesdatefrombritishdate('12 Mar 1917')
        self.assertEqual(mdate, ('12.3.1917', 3, BRITISHTYPE))

    def test_02(self):
        mdate = modesdatefrombritishdate('1917')
        self.assertEqual(mdate, ('1917', 1, MODESTYPE))

    def test_03(self):
        mdate = modesdatefrombritishdate('12.3.1917')
        self.assertEqual(mdate, ('12.3.1917', 3, MODESTYPE))

    def test_04(self):
        mdate = modesdatefrombritishdate('3.1917')
        self.assertEqual(mdate, ('3.1917', 2, MODESTYPE))

    def test_05(self):
        mdate = modesdatefrombritishdate('12 March 1917')
        self.assertEqual(mdate, ('12.3.1917', 3, BRITISHTYPE))

    def test_06(self):
        mdate = modesdatefrombritishdate('March 1917')
        self.assertEqual(mdate, ('3.1917', 2, BRITISHTYPE))

    def test_07(self):
        self.assertRaises(ValueError, modesdatefrombritishdate, 'Mar 12 1917')


if __name__ == '__main__':
    unittest.main()
