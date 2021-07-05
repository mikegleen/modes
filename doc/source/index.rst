.. Modes documentation master file, created by
   sphinx-quickstart on Thu Oct 22 10:05:24 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Modes Python Library
====================

.. toctree::
   :maxdepth: 3

   compare_elts
   csv2xml
   docx2csv
   exhibition
   location
   update_from_csv
   websitecsv
   xml2csv


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


This library provides for manipulation of the XML files exported from
and imported into the *Modes* Museum database system. The source files
contains many special-purpose programs that apply only to the Heath
Robinson Museum database. However, there are several general-purpose
programs that will be documented here.

The Configuration Domain Specific Language (DSL)
------------------------------------------------

A configuration language is defined in YAML syntax that provides
specification of XML fields and control over whether records are
selected for processing.

The configuration consists of a YAML file broken into multiple
documents, separated by lines containing ``---`` in the left three columns.
Each document roughly corresponds to a column to write to the CSV file.
Each document contains some of the following statements. Statements are
case sensitive; all must be lower case. Commands can be
column-generating or control statements.

Statements
~~~~~~~~~~

Single-command Statements
+++++++++++++++++++++++++

-  **cmd** Required. See below for a description of the individual
   commands.
-  **xpath** Required. This describes the XSLT path to a relevant XML
   element.
-  **attribute** Required by the **attrib** and **ifattrib** commands.
-  **title** Optional. If omitted, a best-guess title will be created
   from the xpath statement. If in a control document, this will be
   shown in diagnostics.
-  **value** Required for **ifeq** or **ifattribeq** or **ifcontains**
   or **constant** command.
-  **normalize** Adjust this ID number so that it sorts in numeric
   order.
-  **casesensitive** By default, comparisons are case insensitive.
-  **width** truncate this column to this number of characters
-  **required** Issue an error message if this field is missing or
   empty. Valid only with a control command (**if** ...) or with a
   **column** command in ``csv2xml.py``. In this case it is useful for
   discarding rubbish rows in the CSV file.
-  **multiple_delimiter**  The character to use within a column to separate the
   values when used with the **multiple** command. The statement may
   appear under the **global** command or a specific **multiple** command,
   which takes precedence. The default is "|".

Global-command Statements
+++++++++++++++++++++++++

-  **delimiter** The character to use for the CSV file field
   separator. The default is “,”.
-  **multiple_delimiter**  The character to use within a column to separate the
   values when used with the **multiple** command. The statement may
   appear under the **global** command or a specific **multiple** command,
   which takes precedence. The default is "|".
-  **record_tag** This is the tag (of which there are usually many)
   that will be the root for extracting columns. The default is
   ‘Object’.
-  **record_id_xpath** This is where the ID is found based on the
   root tag. The default is ‘./ObjectIdentity/Number’. In addition to
   being output as column 1 by default, the ID is used in error
   messages.
-  **skip_number** Do not automatically write the serial number as the
   first column. This can be useful when sorting on another column. The
   ID number can be manually inserted as another column.


Commands
~~~~~~~~

Each document has one **cmd** statement, which is usually the first
statement in the document. Column-generating commands are those that map
the document to a corresponding column in the associated CSV file (but see
the **constant** command for an exception).

Column-generating Commands
++++++++++++++++++++++++++

-  **attrib** Like **column** except displays the value of the attribute
   named in the **attribute** statement.
-  **column** This is the basic command to display the text of an
   element.
-  **constant** For ``csv2xml.py``, create an element from the ``value``
   statement of this document without reference to the CSV file.
-  **keyword** Find the element specified by the xpath statement whose text
   equals the text in the value statement and then return the
   first Keyword sub-element's text.
-  **multiple** Like column except it produces a delimiter-separated list of
   values.
-  **count** Displays the number of occurrences of an element under its
   parent.

Control Commands
++++++++++++++++

These commands do not generate output columns.

-  **global** This document contains statements that affect the
   overall output, not just a specific column.
-  **if** Control command that selects an object to display if the
   element text is populated.
-  **ifattrib** Like **if** except tests for an attribute
-  **ifattribeq** Like **ifeq** except compares the value against an
   attribute. Example:

::

       cmd: ifattribeq
       xpath: .
       attribute: elementtype
       value: fine art
       ---

-  **ifcontains** Select an object if the value in the **value**
   statement is contained in the element text.
-  **ifeq** Select an object if the element text equals the **value**
   statement text.

Utility Programs
----------------
All programs are executed by calling:

::

   python src/<name>.py

The appropriate environment must be active. On my system this is done
by calling ``conda activate py8`` prior to calling the program.

:doc:`compare_elts`
~~~~~~~~~~~~~~~~~~~
Compare two elements in the same Object.

:doc:`csv2xml`
~~~~~~~~~~~~~~
Create XML elements from data in a CSV file and a template XML file.

:doc:`docx2csv`
~~~~~~~~~~~~~~~
Read a DOCX file, extract any tables, and convert them to CSV.

:doc:`exhibition`
~~~~~~~~~~~~~~~~~
Import exhibition information into a Modes XML file.

list_by_box
~~~~~~~~~~~
Create a CSV file with the object location as the first field.
Parameters:

1. Input XML file
2. Optional output CSV file. If omitted, output is to STDOUT.

Output must be sorted. The expected use is:

::

   python src/list_by_box.py infile.xml | sort >output.csv

There is no separate documentation page for this program.

:doc:`location`
~~~~~~~~~~~~~~~
Do updating, listing and
validating of object locations. If updating a current location, a
previous location element is created.

:doc:`update_from_csv`
~~~~~~~~~~~~~~~~~~~~~~
Update an XML file driven by a YAML configuration file with
input data from a CSV file.

:doc:`websitecsv`
~~~~~~~~~~~~~~~~~
Utility for recoding fields for loading to the website collection
at heathrobinsonmuseum.org.

:doc:`xml2csv`
~~~~~~~~~~~~~~
Extract
fields from an XML file, creating a CSV file with the fields as
specified in the configuration.
