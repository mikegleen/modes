# -*- coding: utf-8 -*-
"""

"""
import os.path
import unittest
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from xml2csv import main


class TestXml2csv(unittest.TestCase):
    T = True
    F = False
    TESTLOCATION = '/Users/mlg/pyprj/hrm/modes/data/test/xml2csv'
    TESTS = [
        # (test number, expected rows, expected not found, columns in 1st row
        (1, 1, 0, 1),
    ]

    def test_xml2csv(self):
        print('\n')
        for test_tuple in TestXml2csv.TESTFILES:
            testnum, expected_rows, expected_notfound, expected_columns = (
                test_tuple)
            filename = f'test{testnum:02}'
            with self.subTest():
                xmlfilename = os.path.join(TestXml2csv.TESTLOCATION, 'xml',
                                           filename)
                ymlfilename = os.path.join(TestXml2csv.TESTLOCATION, 'yml',
                                           filename)
                csvfilename = os.path.join(TestXml2csv.TESTLOCATION, 'csv',
                                           filename)
                n_lines, not_found = main(xmlfilename, ymlfilename, _args.outfile)


if __name__ == '__main__':
    unittest.main()
