.. data_format.rst


Data Formats
============

Accession Number Formats
------------------------

The earliest and most common accession numbers were those beginning with "JB".
These apply to the Joan Brinsmead gift of many objects that still form the core
of the collection. The numbers bettween 1 and 99 have leading zeros prepended
to three places, so JB1 is recorded as JB001. Objects with numbers greater than
999 are left intact. A similar rule apples to long-term loan objects that have
been accessioned with a format like L001.

You can omit leading zeros in input data. The numbers will be normalized to
be amenable for sorting internally, and when written to an output CSV or XML
file will be restored to the standard format. Thus if you enter L22 in the
CSV file used to create a new object element, it will still be written to the
XML file as L022.

Starting 2018, objects are accessioned using the Collections Trust assigned
code for the Heath Robinson Museum, “LDHRM”. Numbers are of the format::

    LDHRM.2018.1
    LDHRM.2018.1.1

The second example is of a sub-number where many similar objects are grouped
under a single accession number. Leading zeros are not allowed.

Accession Number Expansion
--------------------------

You need to enter accession numbers (often called “serial numbers”) in various
places, for example in CSV files or as parameters to command-line utilities.
Sometimes it is convenient to specify
multiple numbers as one expression, e.g. in one row of a CSV file.
The following format allows this.

Accession numbers can be given with trailing
expansion syntax. For example, JB001-002 will expand to JB001, JB002. The
syntax is flexible in that you can also specify JB001-2 for the same effect.
JB998-1023 also works. White space in the field is ignored.

The following formats are allowed::

    JB002&4&6&...
    JB002,SH2,...
    JB002 - JB004
    SH1-99

You cannot mix the "-" form with the "&"
form in the same range. So::

    JB002-3&5

is illegal but::

    JB002-3,JB005

is legal.


Date Formats
------------

The format used in the Modes XML file is d.m.yyyy. Leading zeros are omitted.
The leading day or day and month may be omitted. If you include the **date**
statement in a column document, additional formats are recognized and converted
to Modes format::

            dd mmm yyyy
            dd month yyyy
            mmm yyyy
            month yyyy
            dd/mm/yyyy
            yyyy-mm-dd (ISO 8601)

"mmm" indicates a three-letter month abbreviation (Jan, Feb, etc. Case is ignored).
"month" indicates a full name. Leading zeros may be omitted. Additionally,
Modes format data is cleaned with any leading zeros removed. 


Output CSV File Formats
-----------------------

In general, the Python CSV software is tolerant of varying input CSV formats.
However, if the CSV file created by, for example, ``xml2csv.py`` is fed to another
program, you must be aware of certain details.

The output file includes line terminators of "\r\n", meaning carriage-return
and line-feed. This is the normal line terminator for Windows systems but not
for Unix-like systems (like MacOs) that expect a single character "\n". If the
output file is being read by Excel, this is ok but if it is being read by
another Unix program like sed or awk then this will cause some bizarre results.

An example awk script that removes the offending "\r" character before adding
a column to the end of the row is::

    awk '{sub("\r$", ""); print $1 ",6"}' tmp/not_dulwich.csv >tmp/not_dulwich2.csv


A version of awk, called goawk, is available that silently handles the different
line endings properly.

A separate issue arises when processing the output CSV file in Excel. The file
is created in UTF-8 format but by default Excel assumes a different format which
varies depending on the platform (Windows or MacOs). To avoid this, a Byte Order
Mark (BOM) can be included at the front of the file using the ``-b`` option in programs
that produce CSV output. This will force Excel to process the CSV file as UTF-8
data. This BOM is recognized by most Windows programs but not Unix-like systems.
So if you are processing the output with a program (other than Excel) on a MacOs
system, do not include the BOM.


