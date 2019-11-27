# -*- coding: utf-8 -*-
"""

"""
import unittest
import yaml
from utl.cfgutil import read_cfg, fieldnames

YAML_CFG = '''
cmd: ifeq
elt: ./Identification/ObjectName[@elementtype="Original Artwork"]/Keyword
value: drawing
column: ./Identification/Title

'''

TEST_XML = '''
<?xml version="1.0" encoding="ASCII"?>
<Interchange><Object elementtype="Original Artwork">
    <ObjectIdentity>
        <Number>JB174</Number>
    </ObjectIdentity>
    <Identification>
        <ObjectName elementtype="Type of Object">
            <Keyword>drawing</Keyword>
        </ObjectName>
        <Title>half title to Act II p29</Title>
        <BriefDescription>Drawing - half title to Act II p29, A Midsummer Night's Dream, 1914</BriefDescription>
    </Identification>
    <ObjectLocation elementtype="normal location">
        <Location>S17</Location>
    </ObjectLocation>
    <ObjectLocation elementtype="current location">
        <Location>JBG</Location>
        <Date>
            <DateBegin>21.11.2019</DateBegin>
        </Date>
        <Reason/>
    </ObjectLocation>
</Object>
'''


class TestCfg(unittest.TestCase):
    def test_column(self):
        data = ('column abc', 'attrib abc, def')
        cfg = read_cfg(data)
        self.assertEqual(len(cfg), 2)


class TestYaml(unittest.TestCase):
    def test_yaml_cfg(self):
        cfg = list(yaml.safe_load_all(YAML_CFG))
        cmds = [c['cmd'] for c in cfg]
        for c in cfg:
            self.assertTrue(c['cmd'] in (''))



if __name__ == '__main__':
    unittest.main()
