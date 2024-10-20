"""
    Test the FILENAMEPAT regular expression used in x053_list_pages.py

    Valid filename prefixes (without the trailing .jpg) can be:

    JB001
    JB001-001  # The corresponding accession number includes the subnumber as JB001.1
    LDHRM.2022.21
    LDHRM.2.22.21-001

"""
import re
import sys
import unittest
from web.x053_list_pages import FILENAMEPAT, FILENAMEPAT2, parse_prefix


class TestFilenamePat(unittest.TestCase):

    def subtest(self, m, accn, subn=None, subn_ab=None, page=None, page_ab=None):
        self.assertNotEqual(m, None)
        self.assertEqual(m['accn'], accn)
        self.assertEqual(m['subn'], subn)
        self.assertEqual(m['subnAB'], subn_ab)
        self.assertEqual(m['page'], page)
        self.assertEqual(m['pageAB'], page_ab)

    def subtest2(self, m, accn, page=None, page_ab=None):
        self.assertNotEqual(m, None)
        self.assertEqual(m['accn'], accn)
        self.assertEqual(m['page'], page)
        self.assertEqual(m['pageAB'], page_ab)

    def subtest3(self, prefix, accn, subn='', subn_ab='', page='',
                 page_ab='', modes_key1=None, modes_key2=None):
        (xaccn, xsubn, xsubn_ab, xpage, xpage_ab, xmodes_key1,
         xmodes_key2) = parse_prefix(prefix)
        self.assertEqual(accn, xaccn)
        self.assertEqual(subn, xsubn)
        self.assertEqual(subn_ab, xsubn_ab)
        self.assertEqual(page, xpage)
        self.assertEqual(page_ab, xpage_ab)
        self.assertEqual(modes_key1, xmodes_key1)
        self.assertEqual(modes_key2, xmodes_key2)

    def test_01(self):
        m = re.match(FILENAMEPAT, 'JB001')
        self.subtest(m, 'JB001')

    def test_02(self):
        m = re.match(FILENAMEPAT, 'JB001-001')
        self.subtest(m, 'JB001', '001')

    def test_03(self):
        m = re.match(FILENAMEPAT, 'JB001-001A')
        self.subtest(m, 'JB001', '001', 'A')

    def test_04(self):
        m = re.match(FILENAMEPAT, 'JB001-001-3')
        self.subtest(m, 'JB001', '001', page='3')

    def test_05(self):
        m = re.match(FILENAMEPAT, 'JB001-001-3A')
        self.subtest(m, 'JB001', '001', page='3', page_ab='A')

    def test_06(self):
        m = re.match(FILENAMEPAT2, 'JB001--3A')
        self.subtest2(m, 'JB001', page='3', page_ab='A')

    def test_07(self):
        m = re.match(FILENAMEPAT2, 'JB001--3C')
        # print(m.groups())
        self.subtest2(m, 'JB001', page='3', page_ab='C')

    def test_08(self):
        m = re.match(FILENAMEPAT2, 'JB001--3c')
        # print(m.groups())
        self.subtest2(m, 'JB001', page='3')

    def test_09(self):
        self.subtest3('JB001', 'JB001', modes_key1='JB001')

    def test_10(self):
        self.subtest3('JB001-001', 'JB001', '001', modes_key1='JB001', modes_key2='JB001.1')

    def test_11(self):
        self.subtest3('JB001-001A', 'JB001', '001', 'A', modes_key1='JB001', modes_key2='JB001.1')

    def test_12(self):
        self.subtest3('JB001-001-3', 'JB001', '001', page='3', modes_key1='JB001', modes_key2='JB001.1')

    def test_13(self):
        self.subtest3('JB001-001-3A', 'JB001', '001', page='3', page_ab='A', modes_key1='JB001', modes_key2='JB001.1')

    def test_14(self):
        self.subtest3('JB001--3', 'JB001', page='3', modes_key1='JB001')

    def test_15(self):
        self.subtest3('JB001--3A', 'JB001', page='3', page_ab='A', modes_key1='JB001')

    def test_16(self):
        self.subtest3('JB001-001-3C', 'JB001', '001', page='3', page_ab='C', modes_key1='JB001', modes_key2='JB001.1')


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    unittest.main()
