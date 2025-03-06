# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars


def get_record_tag(infile):
    """
    Parse a Modes XML file containing Object or template records returning either
    "Object" or "template" and raising a KeyError otherwise.

    :param infile: The XML file containing Object or template repeated element
                   groups.
    :return: the tag of the repeated group.
    """
    # Define the two valid root tags and the associated record tags
    recordtags = {'templates': 'template', 'Interchange': 'Object'}

    with open(infile) as xmlfile:
        event, elem = next(ET.iterparse(xmlfile, events=('start',)))
        tag = elem.tag
    return recordtags[tag]  # barf if the root tag is not "templates" or "Interchange"


