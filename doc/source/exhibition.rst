exhibition
==========

Import exhibition information into a Modes XML file.

Input:
    - exhibition list maintained in ``src/cfg/exhibition_list.py`` (hard-coded
      Python file name)
    - input XML file.
    - CSV file of objects in an exhibition. Optional, see the ``-j`` argument.

The format of the CSV file follows. The accession number is by default in the
first column but the other columns must be specified in the program arguments::

      Accession Number,[Exhibition Number],[Catalogue Number]

The format of the exhibition list is::

    Exhibition Number,Date Begin,Date End,Exhibition Name,Place

In the CSV file, the exhibition number is optional and is ignored if the ``--exhibition``
parameter is given. The accession number in the CSV file or specified as a parameter
may contain a string
specifying multiple numbers of the form JB001-003. Note that leading zeroes are
not significant.

Output: updated XML file

The Exhibition group template is::

        <Exhibition>
            <ExhibitionName />
            <CatalogueNumber />
            <Place />
            <Date>
                <DateBegin />
                <DateEnd />
            </Date>
        </Exhibition>


.. index::
    single: exhibition syntax

.. argparse::
   :filename: ../src/exhibition.py
   :func: getparser
   :prog: exhibition.py

