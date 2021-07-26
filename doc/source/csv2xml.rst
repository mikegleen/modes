.. documentatin


csv2xml
=======

.. argparse::
   :filename: ../src/csv2xml.py
   :func: getparser
   :prog: csv2xml.py

Accession Number Expansion
--------------------------

When specifying an inclusion list, accession numbers can be given with trailing
expansion syntax. For example, JB001-002 will expand to JB001, JB002. The
syntax is flexible in that you can also specify JB001-2 for the same effect.
JB998-1023 also works.

