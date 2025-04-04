"""
Synchronize the normal and pretty XML folders. This assumes a folder structure
as::

    Parent
         |
         |-normal
         |-pretty

Alternatively, there can be a folder under each of the normal and pretty
folders::

    Parent
         |
         |-normal
                |
                current
         |-pretty
                |
                current

The names "pretty" and "normal" are hard-coded but the subpath name, shown
above as "current" is specified by the command line argument --subdir.

    The files in the normal folder are in the form:
        2022-01-01_title.xml
    The corresponding files in the pretty folder are in the form:
        2022-01-01_title_pretty.xml

"""

import argparse
import os
import os.path as op
import sys
import time
import xml.dom.minidom as minidom
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET  # PEP8 doesn't like two uppercase chars

from utl.xmlutil import get_record_tag


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


def onefile(infile_name: str, outfile_name: str, mtime: float,
            make_pretty: bool):
    """

    :param infile_name:
    :param outfile_name:
    :param mtime: timestamp to set the outfile's modify time to
    :param make_pretty:
    :return: None
    """
    trace(2, "From: {}\nTo:  {}", infile_name, outfile_name)
    if _args.dryrun:
        return
    nlines = 0
    t1 = time.perf_counter()
    record_tag = get_record_tag(infile_name)
    is_template = True if record_tag == 'template' else False
    trace(1, 'file {}, record_tag={}', infile_name, record_tag)

    infile = open(infile_name, encoding=_args.input_encoding)
    outfile = open(outfile_name, 'wb')
    if is_template:
        declaration = '<templates application="Object">'
    else:
        declaration = ('<?xml version="1.0" encoding="'
                       f'{_args.output_encoding}"?>\n<Interchange>')
    outfile.write(bytes(declaration, _args.output_encoding))
    if make_pretty:
        outfile.write(b'\n')
    objectlevel = 0
    for event, elem in ET.iterparse(infile, events=('start', 'end')):
        if event == 'start':
            if elem.tag == record_tag:
                objectlevel += 1
            continue
        # It's an "end" event.
        if elem.tag != record_tag:
            continue
        objectlevel -= 1
        if objectlevel:
            continue  # It's not a top level Object.
        elem.text = elem.tail = None
        for e in elem.iter():
            # print(f'{e.tag} "{e.text}" "{e.tail}"')
            if e.text:
                e.text = ' '.join(e.text.strip().split())
            if e.tail:
                e.tail = ' '.join(e.tail.strip().split())
        xmlstring = ET.tostring(elem, encoding=_args.output_encoding,
                                xml_declaration=False)
        if make_pretty:
            reparsed = minidom.parseString(xmlstring)
            prettyxml = reparsed.toprettyxml(indent="\t",
                                             encoding=_args.output_encoding)
            # toprettyxml inserts '<?xml....' at the front. Remove it.
            prettyxml = prettyxml.split(b'\n', 1)[1]
            # minidom converts '"' to '&quot' so let elementtree redo it
            etparsed = ET.fromstring(prettyxml)
            xmlstring = ET.tostring(etparsed, encoding=_args.output_encoding,
                                    xml_declaration=False)
        outfile.write(xmlstring)
        nlines += 1
        if make_pretty:
            outfile.write(b'\n')
        elem.clear()
    if is_template:
        outfile.write(b'</templates>')
    else:
        outfile.write(b'</Interchange>')
    infile.close()
    print(f'updating {outfile_name=}')
    outfile.close()
    # Set the destination modification time to the same as the source file so
    # that subsequent executions of this program don't copy the output file
    # back to the input file.
    os.utime(outfile_name, (mtime, mtime))
    if _args.verbose >= 1:
        elapsed = time.perf_counter() - t1
        s = 's' if nlines > 1 else ''
        print(f'End file {infile_name} -> {outfile_name}\n{nlines} object{s} '
              f'written in {elapsed:.3f} seconds')


def get_mtime(subpath: str) -> (dict[str, float], str):
    """
    For each file in the folder formed by parent/subpath, make an entry in a
    dict with keys being the common part of the file and containing the last
    modified time.
    :param subpath: either 'normal' or 'pretty'
    :return: dictionary of file basenames -> mtime, joined parent/subpath
    """
    path = op.join(_args.parent_dir, subpath, _args.subdir)
    mtime = {}
    for fn in sorted(os.listdir(path)):
        fn = str(fn)  # might be bytes. PyCharm whines.
        if not fn.endswith('.xml'):
            continue
        basefn = os.path.splitext(fn)[0]
        basefn = basefn.removesuffix('_pretty')
        fullfn = op.join(path, fn)
        mtime[basefn] = op.getmtime(fullfn)
    return mtime, path


def select(source_mtime: dict[str, float], dest_mtime: dict[str, float]):
    """

    :param source_mtime:
    :param dest_mtime:
    :return: A list of files to be processed.
    """
    selected = []
    for fn in source_mtime:
        # add 1 second to avoid issues comparing floats
        if (fn not in dest_mtime or
                dest_mtime[fn] + 1. < source_mtime[fn]):
            if fn in dest_mtime:
                trace(2, '{}: source mtime: {}, dest mtime {}', fn,
                      source_mtime[fn], dest_mtime[fn])
            else:
                trace(2, '{}: source mtime: {}, dest not found', fn,
                      source_mtime[fn])
            selected.append(fn)
            trace(3, '    Selecting {}', fn)
    nfiles = len(selected)
    s = 's' if nfiles > 1 else ''
    trace(2, '{} file{} selected.', nfiles, s)
    return selected


def main():
    normal_mtime, normal_path = get_mtime('normal')
    pretty_mtime, pretty_path = get_mtime('pretty')

    trace(1, '\nNormal to Pretty:')
    to_pretty = select(normal_mtime, pretty_mtime)
    for fn in to_pretty:
        from_file = op.join(normal_path, fn + '.xml')
        to_file = op.join(pretty_path, fn + '_pretty.xml')
        onefile(from_file, to_file, mtime=normal_mtime[fn], make_pretty=True)

    trace(1, '\nPretty to Normal:')
    to_normal = select(pretty_mtime, normal_mtime)
    for fn in to_normal:
        from_file = op.join(pretty_path, fn + '_pretty.xml')
        to_file = op.join(normal_path, fn + '.xml')
        onefile(from_file, to_file, mtime=pretty_mtime[fn], make_pretty=False)


def getparser():
    parser = argparse.ArgumentParser(description='''
        Examine two folders named *normal* and *pretty* which are subfolders of the
        folder named in the first parameter. If any files in *pretty* are newer
        than corresponding files in *normal* then those files will be normalized
        into the *normal* folder with the suffix "_pretty" removed from the
        filename. Similarly, new files in *normal* will be prettified into
        folder *pretty*.
        ''')
    parser.add_argument('parent_dir', help='''
        The parent folder containing subfolders "normal" and "pretty" ''')

    parser.add_argument('-d', '--dryrun', action='store_true', help='''
        Print logs but do not process files.
        ''')
    parser.add_argument('-e', '--input_encoding', default=None, help='''
        Set the input encoding. The encoding defaults to UTF-8. If set, you
        must also set --output_encoding.
        ''')
    parser.add_argument('-g', '--output_encoding', default=None, help='''
        Set the output encoding. The encoding defaults to UTF-8. If set, you
        must also set --input_encoding.
        ''')
    parser.add_argument('--subdir', default='', help='''
        If present, this directory is a sub-directory under both the normal and
        pretty directories. 
        ''')
    parser.add_argument('-v', '--verbose', type=int, default=1, help='''
        Set the verbosity. The default is 1 which prints summary information.
        ''')
    return parser


def getargs(argv):
    parser = getparser()
    args = parser.parse_args(args=argv[1:])
    e = args.input_encoding
    g = args.output_encoding
    if (e and not g) or (g and not e):
        raise ValueError(
            'Both input and output encoding must be specified.')
    elif not e:
        args.input_encoding = args.output_encoding = 'UTF-8'
    if args.dryrun:
        args.verbose = max(2, args.verbose)
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 10)
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    _args = getargs(sys.argv)
    main()
