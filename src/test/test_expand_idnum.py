"""

"""
import unittest
from utl.cfgutil import expand_idnum


class TestExpandIDnum(unittest.TestCase):

    def test_01(self):
        idnums = expand_idnum('jb001')
        self.assertNotEqual(idnums, ['JB001'])

    def test_02(self):
        idnums = expand_idnum('JB001')
        self.assertEqual(idnums, ['JB001'])

    def test_03(self):
        idnums = expand_idnum('JB001-2')
        self.assertEqual(idnums, ['JB001', 'JB002'])

    def test_04(self):
        idnums = expand_idnum('JB001-02')
        self.assertEqual(idnums, ['JB001', 'JB002'])

    def test_05(self):
        idnums = expand_idnum('SH1-2')
        self.assertEqual(idnums, ['SH1', 'SH2'])

    def test_06(self):
        idnums = expand_idnum('SH9-10')
        self.assertEqual(idnums, ['SH9', 'SH10'])

    def test_07(self):
        idnums = expand_idnum('JB09-10')
        self.assertEqual(idnums, ['JB09', 'JB10'])

    def test_08(self):
        idnums = expand_idnum('JB08-110')
        target = ['JB08', 'JB09'] + ['JB' + str(n) for n in range(10, 111)]
        self.assertEqual(idnums, target)

    def test_09(self):
        idnums = expand_idnum('JB001-002')
        self.assertEqual(idnums, ['JB001', 'JB002'])

    def test_10(self):
        idnums = expand_idnum('JB08-1110')
        target = ['JB08', 'JB09'] + ['JB' + str(n) for n in range(10, 1111)]
        self.assertEqual(idnums, target)

    def test_11(self):
        idnums = expand_idnum('LDHRM.2021.2-17')
        target = ['LDHRM.2021.' + str(n) for n in range(2, 18)]
        self.assertEqual(idnums, target)


if __name__ == '__main__':
    unittest.main()
