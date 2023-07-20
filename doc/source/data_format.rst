.. data_format.rst


Data Formats
============

Accession Number Formats
------------------------

The earliest and most common accession numbers were those beginning with "JB".
These apply to the Joan Brinsmead gift of many objects that still form the core
of the collection. The numbers bettween 1 and 99 have leading zeroes appended
to three places, so JB1 is recorded as JB001. Objects with numbers greater than
999 are left intact. A similar rule apples to long-term loan objects that have
been accessioned with a format like L001.

You can omit leading zeroes in input data. The numbers will be normalized to
be amenable for sorting internally, and when written to an output CSV or XML
file will be restored to the standard format. Thus if you enter L22 in the
CSV file used to create a new object element, it will still be written to the
XML file as L022.


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
JB998-1023 also works.

The following formats are allowed::

    JB002&4&6&...
    JB002,SH2,...
    JB002 - JB004
    SH1-99

White space in the field is ignored.
