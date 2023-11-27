Utility Programs
----------------

All programs are executed by calling:

::

   python src/<name>.py

The appropriate environment must be active. On my system this is done
by calling ``conda activate py311`` prior to calling the program. If called
without parameters, the program will simulate a ``-h`` parameter and display
the help page.


:doc:`compare_elts`

Compare two elements in the same Object.


:doc:`csv2xml`

Create XML elements from data in a CSV file and a template XML file.

:doc:`docx2csv`

Read a DOCX file, extract any tables, and convert them to CSV.

:doc:`exhibition`

Import exhibition information into a Modes XML file.

:doc:`list_by_box`

Create a report with the object location as the first field.

:doc:`location`

Do updating, listing and
validating of object locations. If updating a current location, a
previous location element is created.

:doc:`recode_collection`

Utility for recoding fields for loading to the website collection
at heathrobinsonmuseum.org.


strip_csv

Remove leading and trailing whitespace from each cell in a CSV file. Two
parameters are required, input and output CSV files.

:doc:`update_from_csv`

Update an XML file driven by a YAML configuration file with
input data from a CSV file.

:doc:`xml2csv`

Extract
fields from an XML file, creating a CSV file with the fields as
specified in the configuration.
