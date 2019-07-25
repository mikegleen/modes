# -*- coding: utf-8 -*-
"""

"""
import unittest

from utl.cfgutil import read_cfg, fieldnames


class TestCfg(unittest.TestCase):
    def test_column(self):
        data = ('column abc', 'attrib abc, def')
        cfg = read_cfg(data)
        self.assertEqual(len(cfg), 2)



if __name__ == '__main__':
    unittest.main()