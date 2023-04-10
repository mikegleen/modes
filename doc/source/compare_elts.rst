compare_elts
============

.. argparse::
   :filename: ../src/compare_elts.py
   :func: getparser
   :prog: compare_elts.py


Specimen Configuration File
---------------------------
This is a typical file used to specify the two fields to compare::

    ---
    cmd: column
    xpath: ./Identification/Title
    title: 'Title'
    ---
    cmd: column
    xpath: ./Identification/BriefDescription
    title: 'Brief Description'
    ---
