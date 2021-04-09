"""

"""
import unittest
from utl.cfgutil import expand_idnum


class TestLocation(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()