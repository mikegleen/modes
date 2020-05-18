# -*- coding: utf-8 -*-
"""

"""
import os.path
import unittest
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from xml2csv import main, getargs


class TestXml2csv(unittest.TestCase):
    TESTLOCATION = '/Users/mlg/pyprj/hrm/modes/test/xml2csv'
    DEFAULT_FIXEDPARAMS = ['--heading', '-v', '0']
    TESTFILES = [
        # (test number, expected rows, expected not found, columns in 1st row
        (1, 1, 0, None),
        (2, 1, 0, None),
        (3, 1, 1, None),
        (4, 1, 0, None),
        (5, 0, 0, None),
        (6, 2, 0, None),
    ]

    def onetest(self, test_tuple):
        (testnum, expected_rows, expected_notfound, fixedparams) = test_tuple
        if fixedparams is None:
            fixedparams = TestXml2csv.DEFAULT_FIXEDPARAMS
        filename = f'test{testnum:02}'
        xmlfilename = os.path.join(TestXml2csv.TESTLOCATION, 'xml',
                                   filename + '.xml')
        ymlfilename = os.path.join(TestXml2csv.TESTLOCATION, 'yml',
                                   filename + '.yml')
        csvfilename = os.path.join(TestXml2csv.TESTLOCATION, 'results',
                                   filename + '.csv')
        params = (['dummy_prog_name', xmlfilename, csvfilename, '-c',
                   ymlfilename] + fixedparams)
        n_rows, n_notfound = main(params)
        self.assertEqual(expected_rows, n_rows,
                         f'Expected rows, actual rows in {filename}')
        self.assertEqual(expected_notfound, n_notfound,
                         f'Expected not found, actual not found in {filename}')

    def test_xml2csv(self):
        print('\n')
        for test_tuple in TestXml2csv.TESTFILES:
            with self.subTest():
                self.onetest(test_tuple)


if __name__ == '__main__':
    unittest.main()
