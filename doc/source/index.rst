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
   list_imgs
   location
   recode_collection
   update_from_csv
   xml2csv
   genindex
   data_format


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


This library provides for manipulation of the XML files exported from
and imported into the *Modes* Museum database system. The source files
contain many special-purpose programs that apply only to the Heath
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
The various programs use the CSV file for slightly different purposes. For example,
``csv2xml.py`` uses it to contain multiple columns each of which defines a value to
go into a corresponding field in the XML file. On the other hand, ``xml2csv.py`` uses
an optional input CSV file of only one column that contains a list of accession
numbers of objects to extract data from.

Each document contains some of the following statements. Statement names are
case sensitive; all must be lower case. The lead statement in a document
is the **cmd** statement, which controls the function of the document.
Commands can be column-related or control statements.

By default, the first column in the output CSV file is the serial number (accession
number) of the object affected. This can be suppressed using the
``skip_number`` statement under the ``global`` command.

Statements
~~~~~~~~~~

Introduction
++++++++++++

Statements can apply to a single document or globally to the whole configuration.

Single-document Statements
++++++++++++++++++++++++++

These are statements that affect a single column-related or control document. The
other class of statements are those that affect the entire process and are under
the ``cmd: global`` document.

-  **attribute** Required by the **attrib** and **ifattrib** commands.
-  **casesensitive** By default, comparisons are case insensitive.
-  **cmd** Required. See below for a description of the individual
   commands.
-  **date** allowed in ``csv2xml.py``. Indicates that a field may be in British
   format, dd mmm yyyy, and should be converted to Modes format. If it is already in Modes
   format, that will be preserved.
-  **element** Referenced when processing the **parent_path** statment for the name
   of the element's tag to be created. If this is omitted the element name will be taken
   from the **title** statment. If both are omitted the name will be taken from the title
   generated from the **xpath** statement.
-  **insert_after** If an element doesn't exist, it will be inserted after the
   element who's simple name is given here. You must also specify **parent_path**.
-  **multiple_delimiter**  The character to use within a column to separate the
   values when used with the **multiple** command. The statement may
   appear under the **global** command or a specific **multiple** command,
   which takes precedence. This statement is also used by the **items** command.
   The default is “|”.
-  **normalize** Adjust this accession number so that it sorts in numeric
   order. The number will be de-normalized before output. The default serial
   number in the first column and the accession number extracted from the XML
   file will always be normalized before use. This may also be used to strip leading
   zeros from another numeric field such as entry numbers.
-  **parent_path** Include this statement if the **xpath** may not
   exist, in which case a new one will be created as a child of this path.
   Implemented in ``csv2xml.py`` and ``update_from_csv.py`` only. The element
   name to be created will be taken from the **element** statement in the document.
   If the **element** statement doesn't exist, the name will be taken from the **title**
   statement in the document. See the **title** statement below. The element named by this
   path must already exist.
-  **required** If this field is missing or
   empty issue an error message and discard the row. Valid only with a control
   command (**if** ...) or with a **column** command in ``csv2xml.py``. In this case it is
   useful for discarding rubbish rows in the CSV file.
-  **title** Optional. If omitted, a best-guess title will be created
   from the xpath statement. If in a control document, this will be
   shown in diagnostics. The titles of documents must be unique. If the ``--heading``
   option is selected in ``update_from_csv.py`` the value of this statement must match
   the heading of the corresponding column in the CSV file.
-  **value** Required for **ifeq** or **ifattribeq** or **ifcontains**
   or **constant** command.
-  **width** truncate this column to this number of characters when writing to
   a CSV file. Ignored when writing to an XML file.
-  **xpath** Required. This describes the XSLT path to a relevant XML
   element.


Global-command Statements
+++++++++++++++++++++++++

These statements are in the document whose ``cmd`` statement is ``global``.

-  **delimiter** The character to use for the CSV file field
   separator. The default is “,”.
-  **multiple_delimiter**  See the description of this command in the
   *Single-command Statements* section.
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
   column of the output row. Note that accession numbers are normally normalized before
   sorting.
-  **add_mda_code** If the serial number does not begin with the MDA code (default LDHRM)
   then insert it as a prefix. This is used only in ``csv2xml.py``
   and ``update_from_csv.py``.
-  **template_title** Only in ``csv2xml.py``: Defines a CSV column containing a key that
   matches one of the keys in the
   global **templates** statement. For each row in the CSV file, this specifies which
   template should be used to create the XML Object element. The default title of the
   column in the CSV file is ``template``. Note that this is case-sensitive.
-  **template_dir** Only in ``csv2xml.py``: This names the path to the directory
   containing the files named in the ``templates`` statement.
-  **templates** Only in ``CSV2XML.py``: This is a complex statement used to map a key
   to a filename. The format of the statement is::

      templates:
         key1: filename1.xml
         key2: filename2.xml

   The keys should be entered in a column specified by ``template_title`` in the CSV file
   specified by ``--incsvfile``.
   See commands ``template_title`` and ``template_dir``. Note that the indentation of the
   "key" rows is mandatory.

Commands
~~~~~~~~

Each document has one **cmd** statement, which is customarily the first
statement in the document. Column-related commands are those that map
the elements in the XML document to a corresponding column in the associated CSV file
(but see the **constant** command for an exception).

Column-related Commands
+++++++++++++++++++++++

-  **attrib** Like **column** except displays the value of the attribute
   named in the **attribute** statement.
-  **column** This is the basic command to display or update the text of an
   element.
-  **constant** For ``csv2xml.py`` and ``update_from_csv.py``, create an element
   from the ``value`` statement of this document without reference to the CSV file.
-  **keyword** Find the element specified by the xpath statement whose text
   equals the text in the **value** statement and then return the
   first Keyword sub-element's text.
-  **items** Used by ``csv2xml.py`` to create ``<Item>`` elements for the multiple
   text strings delimited by the delimiter specified by the **multiple_delimiter**
   statement.
-  **multiple** Used by ``xml2csv.py``. Like the **column** command except it produces a
   delimiter-separated list of values. See the optional **multiple_delimiter** statement.
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
   overall output, not just a specific column. See the section above *Global-command
   Statements*.
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

   This examines the ``elementtype`` attribute on the ``Object`` element.
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


Reserved Words
--------------

The following words are reserved in the CSV file used as input to
``updatefromcsv.py``:

-  **{{clear}}** In ``updatefromcsv.py``, if this appears in a field in the input CSV
   file, then the field in the XML file is cleared. An empty field in the CSV file
   causes no action unless the ``--empty`` or ``--replace`` option is specified.
-  **{{today}}** In ``updatefromcsv.py``, if this appears in a field in the input CSV
   file, then the field is set to the value of ``--date``. The default is today’s date
   if the parameter is not set.

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


Examples
--------
The following examples illustrate various usages of the library.

Insert ``Entry`` Elements
~~~~~~~~~~~~~~~~~~~~~~~~~
Entry numbers are recorded for recent acquisitions. They are recorded in elements such as::

    <Entry>
        <EntryNumber>53</EntryNumber>
    </Entry>

Not all of the elementtype's templates include skeleton Entry/EntryNumber elements so it
may be necessary to create these elements. This may be done with a YAML configuration::

   cmd: global
   add_mda_code:
   ---
   cmd: constant
   xpath: ./Entry
   parent_path: .
   insert_after: Acquisition
   title: Entry
   value:
   ---
   cmd: column
   xpath: ./Entry/EntryNumber
   parent_path: ./Entry
   normalize:

This is matched with an input CSV detail file::

   Serial,EntryNumber
   2018.6,008
   2019.13-43,53
   2019.44,50
   2021.25,58
   2022.23-26,103

The command to effect this update is::

    python src/update_from_csv.py prod_update/normal/2022-08-25_entry.xml \
    prod_update/normal/2022-08-25_entry2.xml -c src/cfg/entry.yml \
    -m data/sally/2022-08-20_object_entry.csv

This illustrates several features.

#. Accession numbers are expressed without leading MDA codes. The global statement
   ``add_mda_code`` forces ``LDHRM.`` to be prepended to the given number.
#. Accession number expansion is used. See :doc:`data_format`.
#. The entry number is sometimes given with leading zeros. These are stripped off
   because of the **normalize** statement in the ``EntryNumber`` column.
#. The ``EntryNumber`` column does not have an explicit title. This is taken from the trailing
   tag in the **xpath** statement.

The script will attempt to insert the new value in an existing ``Entry`` element. If it
doesn't exist, it will search for the parent and create a subelement.
However, that does also not exist. The
solution is to create the parent element first. Normally, this will be created as a new
subelement of *its* parent. This is modified by the **insert_after** statement.
