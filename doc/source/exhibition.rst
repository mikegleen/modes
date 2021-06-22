exhibition
==========

Import exhibition information into a Modes XML file.

::

    Input: - exhibition list maintained in src/cfg/exhibition_list.py
           - input XML file.
           - CSV file of objects in an exhibition. CSV format:
               accession#,[exhibition#]
           The exhibition # is optional and is ignored if the --exhibition
           parameter is given. The accession number may contain a string
           specifying multiple numbers of the form JB001-003.
    Output: updated XML file

    The Exhibition group template is:
        <Exhibition>
            <ExhibitionName />
            <CatalogueNumber />
            <Place />
            <Date>
                <DateBegin />
                <DateEnd />
            </Date>
        </Exhibition>

.. argparse::
   :filename: ../src/exhibition.py
   :func: getparser
   :prog: exhibition.py

