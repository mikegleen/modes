# -*- coding: utf-8 -*-
"""

"""
import os.path
import unittest
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
from location import validate_locations, loc_types


class Aargs:
    """
    Mock args as returned from argparse for testing loc_types
    """
    def __init__(self, clt, c, n, p):
        self.col_loc_type = clt
        self.current = c
        self.normal = n
        self.previous = p


class TestLocation(unittest.TestCase):
    T = True
    F = False
    TESTLOCATION = '/Users/mlg/pyprj/hrm/modes/test/location/xml'
    TESTFILES = [
        ('location_test01.xml', T, '1 normal, 1 current'),
        ('location_test02.xml', F, '1 normal, 2 current'),
        ('location_test03.xml', F, 'dateend present in first current'),
        ('location_test04.xml', F, 'bad  DateBegin'),
        ('location_test05.xml', F, 'missing DateBegin'),
        ('location_test06.xml', F, 'DateEnd missing from old current'),
        ('location_test07.xml', F, 'dates oldest first, missing DateEnd'),
        ('location_test08.xml', F, 'Unexpected ObjectLocation elementtype'),
        ('location_test09.xml', F, 'multiple normal locations'),
        ('location_test10.xml', F, 'missing current location'),
        ('location_test11.xml', T, 'first location is not normal'),
        ('location_test12.xml', F, 'Invalid DateEnd'),
        ('location_test13.xml', F, 'current location with no DateEnd is not '
                                   'the latest.'),
        ('location_test14.xml', F, 'begin date is younger than end date.'),
        ('location_test15.xml', F, 'begin date is not equal previous end'
                                   ' date.'),
        ('location_test16.xml', T, 'previous location precedes current'
                                   ' location.'),
        ('location_test17.xml', F, 'gap between end date and previous begin'
                                   ' date.'),
    ]

    TESTSTRICTFILES = [
        ('location_test17.xml', T, 'gap between end date and previous begin'
                                   ' date.'),
    ]

    TESTLOCTYPES = [

    ]

    def test_loc_types(self):
        newrows = {
            'JB0001021': ('JB1021', 'c', 'FFF'),
            'JB0001022': ('JB1022', 'n', 'FFF'),
            'JB0001023': ('JB1022', 'cn', 'FFF'),
            'JB0001024': ('JB1022', 'C', 'FFF'),
                   }
        for normidnum in newrows:
            with self.subTest(normidnum=normidnum):
                row = newrows[normidnum]
                cnpargs = [eval('TestLocation.' + x) for x in row[2]]
                aargs = Aargs(1, *cnpargs)
                c, n, p = loc_types(row[0], normidnum, aargs, newrows)
                self.assertEqual(c, 'c' in row[1].lower())
                self.assertEqual(n, 'n' in row[1].lower())

    def test_loc_types_a(self):
        newrows = {
            'JB0001025': ('JB1021', '', 'TFF'),
            'JB0001026': ('JB1022', '', 'FTF'),
            'JB0001027': ('JB1022', '', 'FFT'),
                   }
        for normidnum in newrows:
            with self.subTest(normidnum=normidnum):
                row = newrows[normidnum]
                cnpargs = [eval('TestLocation.' + x) for x in row[2]]
                aargs = Aargs(None, *cnpargs)
                print(aargs)
                c, n, p = loc_types(row[0], normidnum, aargs, newrows)
                self.assertEqual(c, cnpargs[0])
                self.assertEqual(n, cnpargs[1])
                self.assertEqual(p, cnpargs[2])

    def test_validate(self):
        print('\n')
        for filename, expected, msg in TestLocation.TESTFILES:
            with self.subTest(filename=filename):
                testfile = os.path.join(TestLocation.TESTLOCATION, filename)
                infile = open(testfile)
                tree = ET.parse(infile)
                elem = tree.find('Object')
                idelem = elem.find('./ObjectIdentity/Number')
                idnum = idelem.text if idelem is not None else None
                result = validate_locations(idnum, elem)
                infile.close()
                if expected:
                    self.assertTrue(result, msg=msg)
                else:
                    self.assertFalse(result, msg=msg)

    def test_validate_no_strict(self):
        print('\n')
        for filename, expected, msg in TestLocation.TESTSTRICTFILES:
            with self.subTest(filename=filename):
                testfile = os.path.join(TestLocation.TESTLOCATION, filename)
                infile = open(testfile)
                tree = ET.parse(infile)
                elem = tree.find('Object')
                idelem = elem.find('./ObjectIdentity/Number')
                idnum = idelem.text if idelem is not None else None
                result = validate_locations(idnum, elem, strict=False)
                infile.close()
                if expected:
                    self.assertTrue(result, msg=msg)
                else:
                    self.assertFalse(result, msg=msg)


if __name__ == '__main__':
    unittest.main()
