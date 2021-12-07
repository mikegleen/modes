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
   recode_collection
   update_from_csv
   xml2csv
   genindex


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
Each document roughly corresponds to a column in the associated CSV file.
Each document contains some of the following statements. Statements are
case sensitive; all must be lower case. Commands can be
column-generating or control statements.

By default, the first column in the CSV file is the serial number (accession
number) of the object affected. On output, this can be suppressed using the
``skip_number`` statement under the ``global`` command.

Statements
~~~~~~~~~~

Single-command Statements
+++++++++++++++++++++++++

-  **cmd** Required. See below for a description of the individual
   commands.
-  **xpath** Required. This describes the XSLT path to a relevant XML
   element. If the path is **filler**, this column will not be copied
   to the XML file by ``update_from_csv.py``. This is useful if the CSV file
   has columns that you need to skip.
-  **parent_path** Include this statement if the **xpath** may not
   exist, in which case a new one will be created as a child of this path.
   Implemented in ``csv2xml.py`` and ``update_from_csv.py`` only. The element
   name to be created will be taken from the title in the document. See the
   **title** statement below. This element named by this path must already exist.
-  **attribute** Required by the **attrib** and **ifattrib** commands.
-  **title** Optional. If omitted, a best-guess title will be created
   from the xpath statement. If in a control document, this will be
   shown in diagnostics. The titles of documents must be unique.
-  **value** Required for **ifeq** or **ifattribeq** or **ifcontains**
   or **constant** command.
-  **normalize** Adjust this accession number so that it sorts in numeric
   order. The number will be de-normalized before output. The default serial
   number in the first column and the accession number extracted from the XML
   file will be normalized before use.
-  **casesensitive** By default, comparisons are case insensitive.
-  **width** truncate this column to this number of characters when writing to
   a CSV file. Ignored when writing to an XML file.
-  **required** Issue an error message if this field is missing or
   empty. Valid only with a control command (**if** ...) or with a
   **column** command in ``csv2xml.py``. In this case it is useful for
   discarding rubbish rows in the CSV file. In ``xml2csv.py`` if a
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
   ``Object``.
-  **record_id_xpath** This is where the ID is found based on the
   root tag. The default is ``./ObjectIdentity/Number``. In addition to
   being output as column 1 by default, the ID is used in error
   messages.
-  **skip_number** Do not automatically write the serial number as the
   first column. This can be useful when sorting on another column. The
   ID number can be manually inserted as another column.
-  **sort_numeric** The default is to sort the output alphabetically.
   This statement directs the sort to be numeric based on the first
   column of the output row.


Commands
~~~~~~~~

Each document has one **cmd** statement, which is customarily the first
statement in the document. Column-generating commands are those that map
the elements in the XML document to a corresponding column in the associated CSV file
(but see the **constant** command for an exception).

Column-generating Commands
++++++++++++++++++++++++++

-  **attrib** Like **column** except displays the value of the attribute
   named in the **attribute** statement.
-  **column** This is the basic command to display or update the text of an
   element.
-  **constant** For ``csv2xml.py`` and ``update_from_csv.py``, create an element
-  from the ``value`` statement of this document without reference to the CSV file.
-  **keyword** Find the element specified by the xpath statement whose text
   equals the text in the **value** statement and then return the
   first Keyword sub-element's text.
-  **multiple** Like column except it produces a delimiter-separated list of
   values. See the optional **multiple_delimiter** statement.
-  **count** Displays the number of occurrences of an element under its
   parent.

Control Commands
++++++++++++++++

These commands do not generate output columns. The **if...** commands are used
by ``xml2csv.py`` and others that read from the XML file to select which
records to output. Multiple **if...** commands may be used; these are
processed in succession and have an **and** relationship, meaning that all of
the tests must succeed for a record to be selected.

-  **global** This document contains statements that affect the
   overall output, not just a specific column.
-  **if** Control command that selects an object to display if the
   element text is populated.
-  **ifnot** Control command that selects an object to display if the
   element text is not populated.
-  **ifattrib** Like **if** except tests for an attribute
-  **ifattribeq** Like **ifeq** except compares the value against an
   attribute. Example::

       cmd: ifattribeq
       xpath: .
       attribute: elementtype
       value: fine art
       ---

-  **ifattribnoteq** Like **ifattribeq** except compares the value against an
   attribute.
-  **ifcontains** Select an object if the value in the **value**
   statement is contained in the element text.
-  **ifelt** Select an object if the element exists, even if the text is empty.
   If the **required** statement is included, this can be used to detect badly
   formed elements.
-  **ifeq** Select an object if the element text equals the **value**
   statement text.
-  **ifnoteq** Select an object if the element text does not equal the
   **value** statement text.


Accession Number Handling
-------------------------
There are three accession number formats in use at the Heath Robinson Museum.

-  The first
   is for objects that are part of the Joan Brinsmead family gift. This is the bulk of the
   collection. Numbers start with "JB" and are followed by a decimal number. Numbers less
   than 100 are zero padded. For example, "JB001"
-  The second is for items from the Simon Heneage estate. These numbers start with "SH"
   followed by decimal numbers without any zero padding. For example, "SH1"
-  The third format follows the Collections Trust standard. This is the MDA code,
   "LDHRM", followed by a full stop, followed by the year, followed by a full stop,
   followed by a serial number, optionally followed by another full stop and sub-serial
   number, all without leading zeros. For example, "LDHRM.2020.1". Utility
   programs provide an option for  overriding the default MDA code.

When read from a CSV file, the XML file, or the command line, accession numbers are
normalized so that numeric fields sort correctly. That is, internally, all numbers
are padded with zeroes. In this way, JB1 and JB001 are treated as the same object.

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
Create a report with the object location as the first field.
Parameters:

1. Input XML file
2. Optional output CSV file. If omitted, output is to STDOUT.

Output is sorted by box and accession number within each box and displayed with
title lines for each box.
There is no separate documentation page for this program.

:doc:`location`
~~~~~~~~~~~~~~~
Do updating, listing and
validating of object locations. If updating a current location, a
previous location element is created.

:doc:`recode_collection`
~~~~~~~~~~~~~~~~~~~~~~~~
Utility for recoding fields for loading to the website collection
at heathrobinsonmuseum.org.

:doc:`update_from_csv`
~~~~~~~~~~~~~~~~~~~~~~
Update an XML file driven by a YAML configuration file with
input data from a CSV file.

:doc:`xml2csv`
~~~~~~~~~~~~~~
Extract
fields from an XML file, creating a CSV file with the fields as
specified in the configuration.
