"""
    Given an xpath, return the Element object. The caller will then typically set the
    text of that element. If necessary, construct the parent elements to contain it.
    The allowed syntax in the xpath is limited to the following cases:

    * a simple tag - If the element exists, it will be returned. If not, the parent will
      be examined and if it exists the a new element will be created and returned.
    * tag[child] - If necessary, a child will be created
    * tag[child="value"] - If necessary, a child will be created
    * tag[@attribute="value"] - If necessary, an attribute will be created.
    * tag[@attribute] - If necessary, an attribute will be created.
"""
import re
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


patstr = r"""(?P<tag>\w*)
             (?P<qual>\[                # section enclosed by "[]"
               (?P<at>@?)               # indicating that the ref is an attribute
                 (
                   (?P<ref>\w+)         # either a child name or attribute
                   (="
                     (?P<val>[^"]+)"    # the attribute or child text value
                   )?
                 )?]
             )?
          """

pat = re.compile(patstr, flags=re.VERBOSE)


def getelt(root: ET.Element, xpath: str, maxcreate=0) -> ET.Element | None:
    """

    :param root: Usually the Object element
    :param xpath: The path to the element we want.
    :param maxcreate: The number of elements to create.
                     0: the element must exist.
                     1: the final element will be created.
                     2: the parent will also be created.
                     >2: further ancestors will be created.
    :return: the element whose path is described or None if the xpath doesn't exist
    """
    elt = root.find(xpath)
    if elt is not None:
        return elt
    if maxcreate <= 0:
        return None
    epath = xpath
    elts = epath.split('/')
    # get the parent
    parentpath = getelt(root, '/'.join(elts[:-1]), maxcreate-1)
    newelt = elts[-1]
    m = pat.match(newelt)
    newtag = m['tag']
    elt = ET.SubElement(parentpath, newtag)
    if m['qual']:
        atsign = m['at']
        ref = m['ref']
        val = m['val']  # if the =... part is not specified, val is None
        if atsign:
            elt.set(ref, val)
        else:
            child = ET.SubElement(elt, ref)
            child.text = val

    return elt


def test1pat(s: str):
    m = pat.match(s)
    print(f'\n{s=}')
    if m:
        print('    tag=', m['tag'])
        print(f'    {m["qual"]=}')
        print('    at=', m['at'])
        print('    ref=', m['ref'])
        print('    val=', m['val'])
    else:
        print('failed', s)


def testpat():
    test1pat('Number')
    test1pat('ObjectLocation[@elementtype]')
    test1pat('ObjectLocation[@elementtype="normal location"]')
    test1pat('Measurement[Part]')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        testpat()
        sys.exit()
    from utl import readers
    ip1 = readers.object_reader(sys.argv[1])
    outfile = open(sys.argv[2], 'wb')
    declaration = f'<?xml version="1.0" encoding="utf-8"?>\n'
    outfile.write(bytes(declaration, encoding="utf-8"))
    outfile.write(b'<Interchange>\n')
    idnum, obj = next(ip1)
    element: ET.Element = getelt(obj, './ObjectIdentity/Number')
    print(element.text)
    element: ET.Element = getelt(obj, './ObjectIdentity/Name')
    element.text = 'Hey You'
    element: ET.Element = getelt(obj, './MyIdentity/Name')
    element.text = 'Hey Me'
    objstr = ET.tostring(obj)
    outfile.write(objstr)
    outfile.write(b'</Interchange>')
