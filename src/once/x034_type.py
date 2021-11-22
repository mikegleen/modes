"""
Convert:
    <Identification>
-->     <ObjectName elementtype="Type of Object">
-->         <Keyword>drawing</Keyword>
-->     </ObjectName>
        <Title>Olivia. 'Well, come again tomorrow; fare thee well.'</Title>
        <BriefDescription>Olivia saying farewell to Viola</BriefDescription>
    </Identification>

to:

    <Identification>
-->  <Type>drawing</Type>
     <Title>Olivia. 'Well, come again tomorrow; fare thee well.'</Title>
     <BriefDescription>Olivia saying farewell to Viola</BriefDescription>
    </Identification>
"""
import argparse
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def one_elt(elt):
    global updated
    if (ident := elt.find('Identification')) is None:
        return
    objname = ident.find("./ObjectName[@elementtype='Type of Object']")
    if objname is None:
        return
    keyword = objname.find('./Keyword')
    keytext = keyword.text if keyword is not None else ''
    ident.remove(objname)
    typeelt = ET.Element('Type')
    typeelt.text = keytext
    ident.insert(0, typeelt)
    updated += 1


def one_object(oldobj):
    """

    :param oldobj: the Object from the old file
    :return: None. The updated object is written to the output XML file.
    """
    global object_number
    numelt = oldobj.find('./ObjectIdentity/Number')
    if numelt is not None:
        object_number = numelt.text
    else:
        object_number = 'Missing'
    trace(2, '**** {}', object_number)
    one_elt(oldobj)
    encoding = 'us-ascii' if _args.ascii else 'utf-8'
    outfile.write(ET.tostring(oldobj, encoding=encoding))


def main():
    outfile.write(b'<?xml version="1.0" encoding="UTF-8"?>\n<Interchange>\n')
    for event, oldobject in ET.iterparse(infile):
        if oldobject.tag != 'Object':
            continue
        one_object(oldobject)
        oldobject.clear()
    outfile.write(b'</Interchange>')


def getargs():
    parser = argparse.ArgumentParser(description='''
        Replace rogue ANSI characters (0x91 - 0x96) with the corresponding
        Unicode characters.
        ''')
    parser.add_argument('infile', help='''
        The input XML file''')
    parser.add_argument('outfile', help='''
        The output XML file.''')
    parser.add_argument('-a', '--ascii', action='store_true', help='''
        Create the output XML file using the us-ascii encoding rather than
        utf-8. This means that non-ascii characters will be encoded with
        sequences such as "&#8220" meaning the left double quote character.
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 9)
    object_number = ''
    _args = getargs()
    infile = open(_args.infile)
    outfile = open(_args.outfile, 'wb')
    updated = 0
    main()
    print(f'{updated} objects updated.')
