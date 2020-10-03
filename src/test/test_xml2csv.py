# -*- coding: utf-8 -*-
"""

"""
import os.path
import unittest
from xml2csv import main


class TestXml2csv(unittest.TestCase):
    longMessage = True


TESTLOCATION = '/Users/mlg/pyprj/hrm/modes/test/xml2csv'
DEFAULT_FIXEDPARAMS = ['--heading', '-v', '0']
TESTFILES = [
    # (test number, expected rows, expected not found, cmd line params
    (1, 1, 0, None),
    (2, 1, 0, None),
    (3, 1, 1, None),
    (4, 1, 0, None),
    (5, 0, 0, None),
    (6, 2, 0, None),
]


def make_onetest(test_tuple):

    def onetest(self):
        (testnum, expected_rows, expected_notfound, fixedparams) = test_tuple
        if fixedparams is None:
            fixedparams = DEFAULT_FIXEDPARAMS
        filename = f'test{testnum:02}'
        xmlfilename = os.path.join(TESTLOCATION, 'xml', filename + '.xml')
        ymlfilename = os.path.join(TESTLOCATION, 'yml', filename + '.yml')
        csvfilename = os.path.join(TESTLOCATION, 'results', filename + '.csv')
        # Simulate sys.argv with the program name as argv[0]. This will be
        # skipped when the main function calls argparse.parser.parse_args
        params = (['dummy_prog_name', xmlfilename, csvfilename, '-c',
                   ymlfilename] + fixedparams)
        n_rows, n_notfound = main(params)
        self.assertEqual(expected_rows, n_rows,
                         f'Expected rows, actual rows in {filename}')
        self.assertEqual(expected_notfound, n_notfound,
                         f'Expected not found, actual not found in {filename}')
    return onetest


def test_xml2csv(self):
    print('\n')


def maintest():
    for test_tuple in TESTFILES:
        onetest_func = make_onetest(test_tuple)
        setattr(TestXml2csv, f'test_{test_tuple[0]:02}', onetest_func)
    unittest.main()


if __name__ == '__main__':
    maintest()
