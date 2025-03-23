"""
    Given an xpath, return the Element object. The caller will then typically set the
    text of that element. If necessary, construct the parent elements to contain it.
    The allowed syntax in the xpath is limited to the following cases:

    * a simple tag - If the element exists, it will be returned. If not, the parent will
      be examined and if it exists the a new element will be created and returned.
    * tag[child="value"] - If necessary, a child will be created
    * tag[@attribute="value"] - If necessary, an attribute will be created.
"""
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET


def getpath(root: ET.Element, xpath: str) -> ET.Element:

    elt = root.find(xpath)
    if elt is not None:
        return elt
    elts = xpath.split('/')

