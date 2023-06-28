# -*- coding: utf-8 -*-
"""

"""
import os.path
import unittest
from xml2csv import main
from utl.cfgutil import expand_idnum


class TestXml2csv(unittest.TestCase):
    longMessage = True

    def test_one_idnum(self):
        idlist = []
        for idnum in IDNUM_TESTS:
            idlist += expand_idnum(idnum)
        self.assertEqual(idlist, IDNUM_RESULTS)


TESTLOCATION = '/Users/mlg/pyprj/hrm/modes/test/xml2csv'
DEFAULT_FIXEDPARAMS = ['--heading', '-v', '0']
VERBOSE_FIXEDPARAMS = ['--heading', '-v', '1']
TESTFILES = [
    # (test number, expected rows, expected not found, cmd line params
    (1, 1, 0, None),  # column
    (2, 1, 0, None),  # column
    (3, 1, 1, None),  # if
    (4, 1, 0, None),  # ifeq
    (5, 0, 0, None),  # ifeq
    (6, 2, 0, None),  # attrib
    (7, 2, 1, None),  # ifnot
    (8, 1, 0, None),  # ifeq
    (9, 3, 1, None),  # ifnoteq
    (10, 3, 1, None),  # ifattrib
    (11, 0, 0, VERBOSE_FIXEDPARAMS),  # ifattribeq
    (12, 1, 1, None),  # ifattribeq
    (13, 3, 1, None),  # ifattribnoteq
    (14, 1, 0, None),  # ifcontains
    (15, 2, 0, None),  # ifelt
    (16, 2, 2, None),  # ifnotelt
]

# IDNUM_TESTS = 'JB001 jb002-3 jb004-05'.split()
IDNUM_TESTS = 'JB021-24'.split()
IDNUM_RESULTS = ['JB021', 'JB022', 'JB023', 'JB024']


def make_onetest(test_tuple):

    def onetest(self):
        testnum, expected_rows_written, expected_notfound, fixedparams = test_tuple
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
        # n_rows:     the number of objects in the input XML file
        # n_written:  the number of objects selected for writing
        # n_notfound: the number of not found elements in the objects
        #             selected for writing
        n_rows, n_written, n_notfound = main(params)
        self.assertEqual(expected_rows_written, n_written,
                         f'Expected rows, actual rows in {filename}')
        self.assertEqual(expected_notfound, n_notfound,
                         f'Expected not found, actual not found in {filename}')

    return onetest


def maintest():
    for test_tuple in TESTFILES:
        onetest_func = make_onetest(test_tuple)
        setattr(TestXml2csv, f'test_{test_tuple[0]:02}', onetest_func)
    unittest.main()


if __name__ == '__main__':
    maintest()
