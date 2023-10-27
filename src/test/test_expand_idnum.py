"""

"""
import sys
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

    def test_12(self):
        idnums = expand_idnum('LDHRM.2021.2&17')
        target = ['LDHRM.2021.2', 'LDHRM.2021.17']
        self.assertEqual(idnums, target)

    def test_13(self):
        idnums = expand_idnum('LDHRM.2021.2 & 17')
        target = ['LDHRM.2021.2', 'LDHRM.2021.17']
        self.assertEqual(idnums, target)

    def test_14(self):
        idnums = expand_idnum('LDHRM.2021.2 & 17,JB001')
        target = ['LDHRM.2021.2', 'LDHRM.2021.17', 'JB001']
        self.assertEqual(idnums, target)

    def test_15(self):
        idnums = expand_idnum('SH1-02')
        self.assertEqual(idnums, ['SH1', 'SH2'])

    def test_16(self):
        idnums = expand_idnum('SH1&2&3')
        self.assertEqual(idnums, ['SH1', 'SH2', 'SH3'])

    def test_17(self):
        idnums = expand_idnum('SH10-3')
        self.assertEqual(idnums, ['SH10', 'SH11', 'SH12', 'SH13'])

    def test_18(self):
        self.assertRaises(ValueError, expand_idnum, 'SH1-1')

    def test_19(self):
        idnums = expand_idnum('SH104-5')
        self.assertEqual(idnums, ['SH104', 'SH105'])

    def test_20(self):
        self.assertRaises(ValueError, expand_idnum, 'SH109-08')

    def test_21(self):
        idnums = expand_idnum('SH104/5')
        self.assertEqual(idnums, ['SH104', 'SH105'])

    def test_23(self):
        idnums = expand_idnum('SH104/6')
        self.assertEqual(idnums, ['SH104', 'SH105', 'SH106'])

    def test_24(self):
        idnums = expand_idnum('SH2&3&1')
        self.assertEqual(idnums, ['SH2', 'SH3', 'SH1'])

    def test_25(self):
        idnums = expand_idnum('SH2-3&1')
        self.assertEqual(idnums, [])

    def test_26(self):
        idnums = expand_idnum('SH2&30&1')
        self.assertEqual(idnums, ['SH2', 'SH30', 'SH1'])

    def test_27(self):
        idnums = expand_idnum('SH10&3')
        self.assertEqual(idnums, ['SH10', 'SH3'])


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    unittest.main()
