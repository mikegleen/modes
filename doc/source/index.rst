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
   utility_functions
   exhibition
   list_elt_type
   list_imgs
   list_needed
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
selected for processing. The language is used for both CSV → XML and XML → CSV
processing. Most but not all of the commands and statements are used for both cases.

The configuration consists of a YAML file broken into multiple
documents, separated by lines containing ``---`` in the left three columns.
Each document roughly corresponds to a column in the associated CSV file.
The various programs use the CSV file for slightly different purposes. For example,
``csv2xml.py`` uses it to contain multiple columns each of which defines a value to
go into a corresponding field in the XML file. On the other hand, ``xml2csv.py`` uses
an optional input CSV file of only one column that contains a list of accession
numbers of objects to extract data from. For more detail, see the documentation
on the individual programs.

Each document contains some of the following statements. Statement names are
case sensitive; all must be lower case. The lead statement in a document
is the **cmd** statement, which controls the function of the document.
Commands can be column-related or control command which determine which objects
are processed. There is also a ``global`` command.

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

-  **attribute** Required by the **attrib** and **ifattrib** commands when used by
   ``xml2csv.py``. If used by ``update_from_csv.py`` and you are creating an element
   using the **parent_path** statement, this will create an attribute and requires a
   **attribute_value** statement.
-  **attribute_value** The value to insert in an attribute created with the **attribute**
   statement.
-  **case_sensitive** By default, comparisons are case insensitive.
-  **child** Used by ``update_from_csv.py`` when ``parent_path`` is specified to force
   creation of a new element. When that element is created, a subelement is also created.
-  **child_value** Make this the text of the newly created subelement.
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
   element who's simple name is given here. You must also specify **parent_path**. If this
   statement is not specified, the new element will be inserted as the parent's last
   subelement. If the statement is specified but the element name parameter is
   left blank, the new element will be inserted as the first subelement.
-  **multiple_delimiter**  The character or characters to use within a column
   to separate the
   values when used with the **multiple** command or the **items** command.
   The statement may appear under the **global** command or a specific command,
   which takes precedence. The default is “|”.
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
-  **person_name** This column contains a name in the form "last, first" or "first last".
   The name will be converted to the "last, first" form. Used by ``csv2xml.py`` and
   ``update_from_csv.py``. Restriction: This will not work for a name with a suffix like
   "Joseph Biden Jr.".
-  **required** If this field is missing or
   empty issue an error message and discard the row. Valid only with a control
   command (**if** ...) or with a **column** command in ``csv2xml.py``. In this case it is
   useful for discarding rubbish rows in the CSV file.
-  **title** Optional. If omitted, a best-guess title will be created
   from the xpath statement, ignoring predicates (expressions within square brackets).
   If in a control document, the title will be shown in diagnostics but is not otherwise
   used. The titles of data-related documents must be unique as this title corresponds to
   a CSV column heading.
-  **value** Required for **ifeq**, **ifnoteq**, **ifattribeq**, **ifcontains**,
   or **constant** command.
-  **width** truncate this column to this number of characters when writing to
   a CSV file. Ignored when writing to an XML file.
-  **xpath** Required. This describes the XSLT path to a relevant XML
   element. In subid mode this is a simple tag name.
-  **xpath2** This describes the XSLT path to a relevant XML element in the case where a
   single column must be stored in two places. Used in ``csv2xml.py``. This is only valid
   for a ``column`` command. You can, for example, create both the ``normal`` and
   ``current`` locations from a single column value.


Global-command Statements
+++++++++++++++++++++++++

These statements are in the document whose ``cmd`` statement is ``global``.

-  **add_mda_code** If the serial number does not begin with the MDA code (default LDHRM)
   then insert it as a prefix. This is used only in ``csv2xml.py``
   and ``update_from_csv.py``.
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
-  **subid_parent** This statement contains the path to the containing element
   for the Item elements we are creating. The presence of this statement triggers
   subid mode. The value usually should be ``ItemList``.
   Serial numbers are expected to contain sub-IDs, for example ``JB1024.1``
   or ``LDHRM.2022.1.12``. The main ID is expected to exist in the XML file. Each
   row in the CSV file will create an Item entry in the main ID's object under an
   ItemList element. The sub-ID
   will become the ListNumber entry. If the number already exists, the record will be
   overwritten, otherwise a new one will be created. The columns in the CSV file will
   become sub-elements under the Item.
-  **subid_grandparent** If the element named in **subid_parent** doesn't exist, it
   will be appended under this element.
-  **template_file** Only in ``csv2xml.py``: This is the file to be used as the template
   for all of the objects to be created. The --template command-line parameter overrides this.
   If this statement or the --template command-line parameter is specified, do not specify other
   tempate-related statements.
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

   The keys should be entered in the CSV file specified by ``--incsvfile`` in a column
   specified by ``template_title``.
   See commands ``template_title`` and ``template_dir``. Note that the indentation of the
   "key" rows in the YAML file is mandatory. The keys in the YAML and CSV files are case
   insensitive.

Commands
~~~~~~~~

Each document has one **cmd** statement, which is customarily the first
statement in the document. Data-related commands are those that map
the elements in the XML document to a corresponding column in the associated CSV file
(but see the **constant** and **delete** commands for exceptions).

Data-related Commands
+++++++++++++++++++++

-  **attrib** Like **column** except displays the value of the attribute
   named in the **attribute** statement.
-  **column** This is the basic command to display or update the text of an
   element.
-  **constant** For ``csv2xml.py`` and ``update_from_csv.py``, create an element
   from the **value** statement of this document without reference to the CSV file.
   You may also use **constant** in ``xml2csv.py`` but you must include an **xpath**
   statement with a value that is used for the heading if no **title** statement
   is specified.
-  **count** Displays the number of occurrences of an element under its
   parent.
-  **delete** For ``update_from_csv.py``. Delete the first element specified by the
   **xpath** statement. If the **delete** command is
   specified, only the **xpath** statement is allowed.
-  **delete_all** Like **delete** except all occurrences of the element are deleted.
-  **items** Used by ``csv2xml.py`` to create ``<Item>`` elements for the multiple
   text strings delimited by the delimiter specified by the **multiple_delimiter**
   statement.
-  **keyword** Find the element specified by the xpath statement whose text
   equals the text in the **value** statement and then return the
   first Keyword sub-element's text.
-  **multiple** Used by ``xml2csv.py``. Like the **column** command except it produces a
   delimiter-separated list of values. See the optional **multiple_delimiter** statement.

Control Commands
++++++++++++++++

These commands do not generate output columns. The **if...** commands are used
by ``xml2csv.py`` and others that read from the XML file to select which
records to output. Multiple **if...** commands may be used; these are
processed in succession and have an **and** relationship, meaning that all of
the tests must succeed for a record to be selected. Note that tests are
case insensitive unless a case_sensitive statement is specified in the
control command document.

-  **global** This document contains statements that affect the
   overall processing, not just a specific column. See the section above *Global-command
   Statements*.
-  **if** Selects an object to display if the element text is populated.
-  **ifnot** Selects an object to display if the element doesn’t exist or the
   text is not populated.
-  **ifattrib** Selects an object if the attribute is present and the value is
   populated. Requires an **attribute** statement.
-  **ifattribeq** Like **ifeq** except compares the value against an
   attribute. Example::

       cmd: ifattribeq
       xpath: .
       attribute: elementtype
       value: fine art
       ---

   This examines the ``elementtype`` attribute on the ``Object`` element.
-  **ifattribnoteq** Like **ifnoteq** except compares the value against an
   attribute.
-  **ifcontains** Select an object if the value in the **value**
   statement is contained in the element text.
-  **ifelt** Select an object if the element exists, even if the text is empty.
   If the **required** statement is included, a warning message is issued.
-  **ifnotelt** Select an object if the element doesn’t exist.
-  **ifeq** Select an object if the element text equals the **value**
   statement text. Returns false if the element doesn’t exist.
-  **ifnoteq** Select an object if the element text does not equal the
   **value** statement text.

The **global** Command
++++++++++++++++++++++

-  **global** This document contains statements that affect the
   overall processing, not just a specific column. See the section above *Global-command
   Statements*. Some of the statements affect the entire process, like **delimiter**.
   Some of the statements affect the individual columns in the associated CSV file and
   may be overriden by the same named statement in individual documents.


Accession Number Handling
-------------------------
There are four accession number formats in use at the Heath Robinson Museum.

-  The first
   is for objects that are part of the Joan Brinsmead family gift. This is the bulk of the
   collection. Numbers start with "JB" and are followed by a decimal number. Numbers less
   than 100 are zero padded. For example, "JB001"
-  The second is for items from the Simon Heneage estate. These numbers start with "SH"
   followed by decimal numbers without any zero padding. For example, "SH1"
-  The third format follows the Collections Trust standard. This is the MDA code,
   by default "LDHRM", followed by a full stop, followed by the year, followed by a full
   stop, followed by a serial number, optionally followed by another full stop and item
   number, all without leading zeros. For example, "LDHRM.2020.1". Utility
   programs provide an option for overriding the default MDA code.
-  The fourth format is for long-term loans to the museum. These are handled like the JB
   numbers and are padded to three columns of digits, like "L001".

When read from a CSV file, the XML file, or the command line, accession numbers are
normalized so that numeric fields sort correctly. That is, internally, all numbers
are padded with zeroes. In this way, JB1 and JB001 are treated as the same object.

When reading from a CSV file, the MDA code may be omitted (see the global command
``add_mda_code``). Accession numbers that start with a digit will have the MDA code added
as a prefix.


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
by calling ``conda activate py311`` prior to calling the program.

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
However, that also does not exist. The
solution is to create the parent element first. Normally, this will be created as a new
subelement of *its* parent. This is modified by the **insert_after** statement.

Insert an ``Association`` Element Group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When an object is associated with an event or person, it is recorded here. This update
adds an *Association* group recording a donation linked to individual objects.
The association is recorded as::

    <Association>
        <Type>Adopt a Picture</Type>
        <Person>
            <Name>Bloggs, Joe</Name>
        </Person>
        <SummaryText>
            <Keyword>dedication</Keyword>
            <Note>In memory of Jack and Jill Bloggs</Note>
        </SummaryText>
        <Date>25.6.2022</Date>
    </Association>

The data to create this element group is from the CSV file::

    Name,Date,Dedication,Accn. No.
    Joe Bloggs,25 June 2022,"In memory of Jack and Jill Bloggs",LDHRM.2022.999

This element group is created with the following YAML statements. The numbering has
been added as comments to assist this discussion::

    # 1
    cmd: constant
    xpath: ./Association[Type="Adopt a Picture"]
    parent_path: .
    title: Association
    child: Type
    child_value: Adopt a Picture
    value:
    ---
    # 2
    cmd: constant
    xpath: ./Association[Type="Adopt a Picture"]/Person
    parent_path: ./Association[Type="Adopt a Picture"]
    value:
    ---
    # 3
    cmd: column
    xpath: ./Association[Type="Adopt a Picture"]/Person/PersonName
    parent_path: ./Association[Type="Adopt a Picture"]/Person
    title: Name
    person_name:
    ---
    # 4
    cmd: constant
    xpath: ./Association[Type="Adopt a Picture"]/SummaryText
    parent_path: ./Association[Type="Adopt a Picture"]
    value:
    ---
    # 5
    cmd: constant
    xpath: ./Association[Type="Adopt a Picture"]/SummaryText/Keyword
    parent_path: ./Association[Type="Adopt a Picture"]/SummaryText
    value: dedication
    ---
    # 6
    cmd: column
    xpath: ./Association[Type="Adopt a Picture"]/SummaryText/Note
    parent_path: ./Association[Type="Adopt a Picture"]/SummaryText
    title: Dedication
    element: Note
    ---
    # 7
    cmd: column
    xpath: ./Association[Type="Adopt a Picture"]/Date
    parent_path: ./Association[Type="Adopt a Picture"]
    date:
    ---

The first command searches for an *Association* element that has a child *Type* element
containing text ``Adopt a Picture``. In this case we expect it to not be found so it will
be created. Because we know that it doesn't already exist, we could have left out the
``Type=`` clause in the xpath, but it is included to avoid confusion. The **child:** and
**child_value:** statements in this document will create the subelement with tag *Type*
and text ``Adopt a Picture``. The **value:** statement is mandatory with a **constant**
command but is left empty resulting in no text in the ``Association`` element. The text
will appear in the child element, ``Type``.

Command # 2 creates a *Person* element with no text. Command # 3 creates a *PersonName*
subelement to the newly created *Person* element containing text from the **Name** column
in the CSV file. The **person_name:** statement causes the name to be converted to
"lastname, firstname" format.

Commands # 4, 5, and 6 similarly create *SummaryText/Keyword* and *SummaryText/Note*
elements. Command # 6 contains the **element:** statement to designate the subelement
name to be created. If it was not specified, then the element would be *Dedication* taken
from the **title:** statment. The **title:** is ``Dedication`` because that is the heading
of the corresponding column in the CSV file.

Command # 7 creates a *Date* subelement. The **date:** statement says to convert the
date to standard Modes format of dd.mm.yyyy.

The shell command to effect this update is::

    python src/update_from_csv.py\
    prod_update/normal/2022-10-31_loc_JB010.xml\
    prod_update/normal/2022-11-01_adopt.xml\
    -c src/cfg/y010_adopt_a_picture.yml\
    -m results/csv/sally/pictures_adopted.csv\
    --serial 'Accn. No.' -a


Insert an element with Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We want to create a complete element group under the ``Object`` element with
an attribute of elementtype. In this case, the template for the Object was
``reproduction`` which does not include a ``References`` group. The
resultant element group is like::

       <References>
           <Reference elementtype="First Published In">
               <Title>Child’s Arabian Nights: The fisherman</Title>
               <Page>Frontis</Page>
           </Reference>
       </References>


The following is an edited copy of ``.../modes/bin/update/2023-06-12_canprints.sh``::

   #!/bin/zsh
   INXML=2023-05-21_loc.xml
   OUTXML=2023-06-12_canprints.xml
   cat >tmp/update.csv <<EOF
   Serial,Story,Page
   2022.11,Child’s Arabian Nights: The fisherman,Frontis
   ...
   2022.22,Child’s Arabian Nights: The fish bone,p.80
   EOF
   cat >tmp/update.yml <<EOF
   # 1
   cmd: global
   add_mda_code:
   ---
   # 2
   cmd: constant
   xpath: ./References
   parent_path: .
   insert_after: Reproduction
   value:
   ---
   # 3
   cmd: constant
   xpath: ./References/Reference
   parent_path: ./References
   attribute: elementtype
   attribute_value: "First Published In"
   value:
   ---
   # 4
   cmd: column
   xpath: ./References/Reference/Title
   parent_path: ./References/Reference
   title: Story
   element: Title
   ---
   # 5
   cmd: column
   xpath: ./References/Reference/Page
   parent_path: ./References/Reference
   ---
   EOF
   python src/update_from_csv.py prod_update/normal/$INXML \
                                 prod_update/normal/$OUTXML \
                                 -c tmp/update.yml -m tmp/update.csv -r -a -v 2
   bin/syncprod.sh

The first command, *global*, contains the *add_mda_code* statement, required because the given
serial numbers were missing the leading ``LDHRM`` prefix.

Command # 2 creates the initial *References* group. The *value* statement is
required but is left empty. Note that the *insert_after* statement contains
a simple tag name, not an XPATH.

Command # 3 creates the *Reference* element with the
attribute ``elementtype="First Published In"``.

Commands # 4 and 5 create the sub-elements containing the actual data from the
CSV file. In #4, the *title* statement indicates the CSV file column to fetch
the data from and the *element* statement indicates the name of the element to
create. This is required as it would otherwise be "Story", taken from the *title*
statement.


Inserting Sub-IDs
~~~~~~~~~~~~~~~~~

This is a special mode in ``update_from_csv.py`` wherein all of the rows in the
input CSV file contain serial numbers which specify sub-IDs. Examples are::

   JB1204.10
   LDHRM.2022.10.4

In each case there is an extra field at the end of the ID. This field must be
numeric. This mode is enabled by the global statement **subid_parent** which
must contain the path to the parent element of the Item elements to be inserted
for the new subIDs.



