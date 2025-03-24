"""
    Given an xpath, return the Element object. The caller will then typically set the
    text of that element. If necessary, construct the parent elements to contain it.
    The allowed syntax in the xpath is limited to the following cases:

    * a simple tag - If the element exists, it will be returned. If not, the parent will
      be examined and if it exists the a new element will be created and returned.
    * tag[child="value"] - If necessary, a child will be created
    * tag[@attribute="value"] - If necessary, an attribute will be created.
"""
import sys
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def getelt(root: ET.Element, xpath: str) -> ET.Element:
    """

    :param root:
    :param xpath:
    :return: the element whose path is described
    """

    elt = root.find(xpath)
    if elt is not None:
        return elt
    epath = xpath
    elts = epath.split('/')
    # get the parent
    parentpath = getelt(root, '/'.join(elts[:-1]))
    elt = ET.SubElement(parentpath, elts[-1])
    return elt


if __name__ == '__main__':
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
