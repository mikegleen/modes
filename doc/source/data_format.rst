.. data_format.rst


Data Formats
============

Accession Number Expansion
--------------------------

You need to enter accession numbers (often called “serial numbers”) in various places, for
example in CSV files or as parameters to utilities. Sometimes it is convenient to specify
multiple numbers as one expression, e.g. one row of a CSV file.
The following format allow this.

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
