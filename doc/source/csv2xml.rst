csv2xml
=======

.. argparse::
   :filename: ../src/csv2xml.py
   :func: getparser
   :prog: csv2xml.py

Using Multiple Templates
------------------------

Each object element group created from a row in the input CSV file requires a template
containing a skeleton XML structure to populate. The template to be used for all objects can be defined using the :ref:`template_file`
global statement. If different rows require different templates then use the :ref:`template_title` statement to specify
the column in the CSV file to contain a template key, the :ref:`template_dir` statement to specify the directory
containing all of the template files, and the :ref:`templates` structured statement to map the template key to its
corresponding tempate file. For example::

    cmd: global
    template_title: Template
    template_dir: templates/normal
    templates:
      Book: book_template.xml
      original_artwork: Original_Artwork_template.xml
      ephemera: ephemera_template.xml
      decorative_art: decorative_art_template.xml
      reproduction: reproduction_template.xml
      Cutting: cutting_template.xml
    ---

