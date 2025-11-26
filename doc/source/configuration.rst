.. _configuration:

configuration
=============

.. contents::

The Configuration Domain Specific Language (DSL)
------------------------------------------------

   Format conventions:

-   *Italics*    - XML element names
-    **Bold**     - Commands
-    **Bold:**    - Statements
-    ``Monotype`` - file names, parameters (like ``--verbose``)


A configuration language is defined in YAML syntax that provides
specification of XML fields and control over whether records are
selected for processing. The language is used for processing
of CSV → XML, XML → CSV, and XML → XML (with updates from a CSV file).
Most but not all of the commands and statements are used for all cases.

The configuration consists of a YAML file broken into multiple sections
(called *documents*) separated by lines containing ``---`` in the left three columns.
Documents are control documents, column documents, or special documents. The special
documents are **global** and **location**.
Each column document corresponds to a column in the associated CSV file, although there are
exceptions. The “control”
document directs the selection of records (the if... commands).
The various programs use the CSV file for slightly different purposes. For example,
``csv2xml.py`` uses it to contain multiple columns each of which defines a value to
go into a corresponding field in the XML file. On the other hand, ``xml2csv.py`` uses
an optional input CSV file of only one column that contains a list of accession
numbers of objects to extract data from. For more detail, see the documentation
on the individual programs.

Each document contains some of the following statements. Statement names are
case sensitive; all must be lower case. The lead statement in a document
is the **cmd:** statement, which controls the function of the document.
Commands can be column-related or control commands which determine which objects
are processed. There is also a **global** command.

When creating a CSV file, by default the first column is the serial number
(accession number) of the object affected. This can be suppressed using the
**skip_number:** statement under the **global** command.

Statements
~~~~~~~~~~

Introduction
++++++++++++

Statements can apply to a single document or globally to the whole configuration.
Some statements require an argument and others are logical flags that select
a particular behavior.

Single-document Statements
++++++++++++++++++++++++++

These are statements that affect a single column-related or control document. The
other class of statements are those that affect the entire process and are under
the ``cmd: global`` document.

-  **aspect:**

   Used by ``update_from_csv.py``. The argument of the **aspect:** statement
   is the text of a *Keyword* subelement. If an *Aspect* element group exists
   whose subelement *Keyword* text equals the argument, the subelement *Reading*
   text is updated with the **column** command's column value or with the **constant**
   command's **value:**
   statement's argument. If no matching *Aspect* element group exists, then
   an *Aspect* with an empty *Keyword* subelement is overwritten or a new *Aspect*
   element group is created.

   Note that the document’s **xpath:** points to the parent of the *Aspect* being updated.

   For example, given a configuration::

      cmd: constant
      aspect: display order
      xpath: ./Description
      value: 9

   This will create an *Aspect* element group of::

      <Object>
         ...
         ...
         <Description>
            ...
            ...
            <Aspect>
               <Keyword>display order</Keyword>
               <Reading>9</Reading>
            </Aspect>
         </Description>
      </Object>

-  **attribute:**

   Required by the **attrib** and **ifattrib** commands when used by
   ``xml2csv.py``. If used by ``csv2xml.py`` or ``update_from_csv.py`` and you
   are creating an element using the **parent_path:** statement, this will create
   an attribute and requires an **attribute_value:** statement.
-  **attribute_value:**

   The value to insert in an attribute created with the **attribute:**
   statement.
-  **case_sensitive:**

   By default, comparisons are case insensitive.
-  **child:**

   Used by ``update_from_csv.py`` when **parent_path:** is specified to force
   creation of a new element. When that element is created, a subelement of that element is also created.
   The tag of the new subelement is the value of this statement.
-  **child_value:**

   Make this the text of the newly created subelement.
-  **cmd:**

   Required. But see the **column:** statement for an exception.
   See below for a description of the individual commands.
-  **column:**

   This statement is a shortcut for creating two commands::

        column: Date

   will create two statements::

        cmd: column
        title: Date

   Do not use both the **column:** statement and the **cmd:** statement within
   a single document. (Remember, a configuation file consists of multiple
   documents separated by ``---`` lines).
-  **column_title:**

   Normally, the column title is taken from the **title:** statement. However,
   this must be unique so
   if you want the same column to behave differently depending upon **if_other_column:**
   and **if_other_column_value:** values, then specify the column title with this statement.
-  **copy_column:**

   For use in the **copy** command. See that command for the usage.
-  **date:**

   If specified, indicates that a field may be in date
   format and should be converted to Modes format. See the section *Date Formats*
   in the document page *Data Formats* for the formats supported. Allowed in ``csv2xml.py``.
   Also used in ``update_from_csv.py`` with the **location** command.
-  **denormalize:**

   See **normalize:**. If a value has been normalized, it will be output as
   normalized. Include this statement to force denormalization of the field on
   output. Note that normalizing then denormalizing does not necessarily return
   the field to its original form. For example, a number like ``2018.2`` will
   be output with an MDA code prepended.
-  **element:**

   Referenced when processing the **parent_path:** statement for the name
   of the element's tag to be created. If this is omitted the element name will be taken
   from the **xpath:** statment. You should use this, for example, if a parent path
   includes a selector in square brackets such as::

      xpath: ./Association[Type="Adopt a Picture"]

   In the above example, if the **element:** statement is omitted, one will be
   created from the **xpath:** statement by removing the selector::

      element: Association

- **group:**

   Used by **if**, **ifnot**, and **column** commands to indicate that the text
   from the named element and all of its descendents are to be examined instead
   of just the named elemennt’s text.

   The optional parameter is the delimiter character or characters to be used to separate the text fields
   from the individual sub-elements. The default is an empty string.

   Enclose the character in quote marks.
- **if_other_column:**

   Used by ``csv2xml.py``. Process this column if one of the values in the
   **if_other_column_value:** statement matches the value in the column named in the
   **if_other_column:** statement. The values are separated by a "|" character. Leading
   and trailing spaces are ignored. If the **if_other_column_value:** statement
   is omitted, then process this column if the other column is populated in this
   row. For example::

      cmd: column
      title: Artist
      if_other_column: Template
      if_column_value: Artwork | Reproduction
      xpath: ...
      ---

-  **if_other_column_value:**

   Used in conjunction with the **if_other_column:** statement. See above.
- **if_template:**

   This a a shortcut command to be used when there is a **template_title:** statement
   in the **global** command. For example, given a **global** command containing::

      cmd: global
      ...
      template_title: my_template
      ---

   the following document::

      column: Artist
      if_template: Artwork
      xpath: ...
      ---

   will be converted to::

      column: Artist
      if_other_column: my_template
      if_column_value: Artwork
      xpath: ...
      ---

   As with all column titles, the template name is case sensitive.
-  **insert_after:**

   If an element doesn't exist, it will be inserted after the
   element who's simple name is given here. You must also specify **parent_path:**. If this
   statement is not specified, the new element will be inserted as the parent's last
   subelement. If the statement is specified but the element name parameter is
   left blank, the new element will be inserted as the first subelement.
-  **multiple_delimiter:**

   The character or characters to use within a column to separate the
   values when used with the **multiple:** command or the **items:** command.
   The statement may appear under the **global** command or a specific command,
   which takes precedence. The default is “|”.
-  **normalize:**

   If specified, adjust this accession number so that it sorts in numeric
   order. The number will be normalized in the output. The default serial
   number in the first column and the accession number extracted from the XML
   file will always be normalized before use and denormalized before output.
   This may also be used to strip leading zeros from another numeric field such
   as entry numbers. See **denormalize:**.
-  **parent_path:**

   Include this statement if the **xpath:** may not
   exist, in which case a new one will be created as a child of this path.
   Implemented in ``csv2xml.py`` and ``update_from_csv.py`` only. The element
   name to be created will be taken from the **element:** statement in the document.
   If the **element:** statement doesn't exist, the name will be taken from the **xpath:**
   statement in the document. The element named by this
   path must already exist.
-  **person_name:**

   If specified, this column contains a name in the form
   "last, first" or "first last". The name will be converted to the
   "last, first" form. Used by ``csv2xml.py`` and ``update_from_csv.py``.
   Restriction: This will not work for a name with a suffix like "Joseph Biden Jr.".
-  **required:**

   If specified then issue an error message and discard the row if
   this field is missing or empty. Valid only with a control
   command (**if** ...) or with a **column** command in ``csv2xml.py``. In this
   case it is useful for discarding rubbish rows in the CSV file.
-  **title:**

   Optional. Specify the column title in the first row of the CSV file,
   but see the ``--skip_rows`` command line parameter.
   If omitted, a best-guess title will be created
   from the **xpath** statement, which see for an example.
   If in a control document, the title will be shown in diagnostics but is not otherwise
   used. The titles of documents must be unique and are case sensitive.
-  **value:**

   Required for **ifeq**, **ifnoteq**, **ifattribeq**, **ifcontains**, **ifanyeq**,
   **ifnotanyeq**, or **constant** command.
-  **width:**

   truncate this column to this number of characters when writing to
   a CSV file. Ignored when writing to an XML file. The default is to not
   truncate the data in the column.
-  **xpath:**

   Required. This describes the XSLT path to a relevant XML
   element. In subid mode this is a simple tag name.

   If no **title** statement is specified, the title of the CSV column associated
   with this document is generated from the **xpath** statement. For example::

      xpath: ./Description/Measurement[Part="Image"]/Reading

   will generate a title of ``Reading``.
-  **xpath2:**

   This describes the XSLT path to a relevant XML element in the case where a
   single column must be stored in two places. Used in ``csv2xml.py``. This is only valid
   for a **column** command. You can, for example, create both the ``normal`` and
   ``current`` locations from a single column value.


.. _global_command:

Global-command Statements
+++++++++++++++++++++++++

These statements are in the document whose **cmd:** is **global**.

-  **add_mda_code:**

   If the serial number does not begin with the MDA code (default LDHRM)
   then insert it as a prefix. This is used only in ``csv2xml.py``
   and ``update_from_csv.py``. You can specify an MDA code on the command line
   using the --mdacode argument.
-  **delimiter:**

   The character to use for the CSV file field
   separator. The default is “,”.

   Enclose the character in quote marks as some characters are recognized
   by YAML as having semantic meaning.
-  **multiple_delimiter:**

   See the description of this command in the
   *Single-command Statements* section.
-  **prefixes**

   This statement specifies the zero padding to be applied to accession numbers
   with specific prefixes. For example, the accession number "JB001" has a prefix
   of "JB" and a zero padding of three columns. For the Heath Robinson Museum,
   the default setting is equivalent to the following configuration::

       prefixes:
          JB: 3
          L: 3
          sh: 0

   Any prefix not defined in the configuration will have no zero padding. So in
   the above example, the SH entry is redundant. Values specified in the configuration
   will override the default values. The prefixes are coerced to upper case.
-  **record_tag:**

   This is the tag (of which there are usually many)
   that will be the root for extracting columns. The default is
   ``Object``.
-  **record_id_xpath:**

   This is where the ID is found based on the
   root tag. The default is ``./ObjectIdentity/Number``. In addition to
   being output as column 1 by default, the ID is used in error
   messages.
-  **serial:**

   This is the column title of the column to use for the accession number. The
   default value is ``Serial`` (case sensitive). If this statement is specified,
   the command line parameter ``--serial`` is ignored.
-  **skip_number:**

   If specified, do not automatically write the serial number as the
   first column. This can be useful when sorting on another column. The
   ID number can be manually inserted as another column.
-  **sort_numeric**

   The default is to sort the output alphabetically.
   This statement directs the sort to be numeric based on the first
   column of the output row. Note that accession numbers are normally normalized before
   sorting and should be sorted alphabetically.
-  **subid_parent:**

   This statement contains the path to the containing element
   for the Item elements we are creating. The presence of this statement triggers
   subid mode. The value usually should be ``ItemList``.
   Serial numbers are expected to contain sub-IDs, for example ``JB1024.1``
   or ``LDHRM.2022.1.12``. The main ID, for example ``JB1024``, is expected to
   exist in the XML file. Each row in the CSV file will create an Item entry in
   the main ID's object under an ItemList element. The sub-ID
   will become the ListNumber entry. If the number already exists, the record will be
   overwritten, otherwise a new one will be created. The columns in the CSV file will
   become sub-elements under the Item.
-  **subid_grandparent:**

   If the element named in **subid_parent:** doesn't exist, it
   will be appended under this element. Required if **subid_parent:** is specified.
-  **template_file:**

   Only in ``csv2xml.py``: This is the file to be used as the template
   for all of the objects to be created. To specify different template files for different
   types of object, see the other template related statements below.

   The ``--template`` command-line parameter overrides this statement.
   If this statement or the ``--template`` command-line parameter is specified,
   do not specify other tempate-related statements.
-  **template_title:**

   Only in ``csv2xml.py``: Defines a CSV column containing a key that
   matches one of the keys in the
   global **templates:** statement. For each row in the CSV file, this specifies which
   template should be used to create the XML Object element. The default title of the
   column in the CSV file is ``template``. Note that this is case-sensitive.
-  **template_dir:**

   Only in ``csv2xml.py``: This names the path to the directory
   containing the files named in the ``templates`` statement.
-  **templates:**

   Only in ``csv2xml.py``: This is a complex statement used to map keys
   to filenames. The format of the statement is::

      templates:
         key1: filename1.xml
         key2: filename2.xml

   The keys should be entered in the CSV file specified by ``--incsvfile`` in a column
   specified by **template_title:**.
   See commands **template_title:** and **template_dir:**. Note that the indentation of the
   "key" rows in the YAML file is mandatory. The keys in the YAML and CSV files are case
   insensitive. Do not use this statement and also the **template_file:** statement.

.. _location_command_statements:

Location-command Statements
+++++++++++++++++++++++++++

The following statements are either unique to the **location** command or are used in
a different way from their use with, for example, the **column** command.

-  **date:**

   The parameter is the modes-format (d.m.yyyy) date to be inserted as the
   *DateEnd* field of the now previous location and the *DateBegin* field of the new
   current location. If not included, the value of the ``--date`` parameter is used.
-  **reason:**

   The parameter is text to be entered in the *Reason* field of the location
   element.
-  **location_type:**

   You can update the normal location, the current location, or both. You can also
   move the current location to the normal location. The syntax is best explained by
   examples::

      location_type: normal
      location_type: current
      location_type: current normal
      location_type: normal current
      location_type: move_to_normal

   Parameters can be abbreviated to the first letter.
-  **location_column:**

   This indicates the column in the CSV file containing the new location. You must
   include either this statement or a **value:** statement. If both are included then
   the new location will be taken from the field in the CSV file unless it
   is empty in which case the value from the **value:** statement will be used.

   If there is no **value:** statement, an empty field in the CSV file is an error.
-  **title:**

   Optional. Each document requires a unique title. If this statement is not included, a title will be taken
   from the **location_column:** statement if it exists. Otherwise a default of "Location" will be used.

   This statement is only needed in the rare case that there is a CSV column entitled "Location" other than
   the column named in the **location_column:** statement.
-  **value:**

   The new location to be inserted in all objects updated. See the **location_column:** statement above for more
   details.

Commands
~~~~~~~~

Each document has one **cmd:** statement, which is customarily the first
statement in the document. The **cmd:** statement can either be explicitly
written or generated internally by a **column:** statement.

Data-related Commands
+++++++++++++++++++++

Data-related commands are those that map
the elements in the XML document to a corresponding column in the associated CSV file
(but see the **location**, **constant**, and **delete** commands for exceptions).

-  **cmd: attrib**

   Like **column** except displays the value of the attribute
   named in the **attribute:** statement. For ``xml2csv.py`` only.
-  **cmd: column**

   This is the basic command to display or update the text of an
   element. When inserting into an XML field, you can control various features.
   By default, values are only inserted into an XML field if that field is
   unpopulated. Specify ``--replace`` to override this. By default, if a field
   in the CSV file is empty, no action takes place. Specify ``--empty`` to
   override this. Note ``--empty`` implies ``--replace``. See the section
   :ref:`Reserved Words` for other actions.

   You must specify a title explicitly with the **title:** statement or implicitly
   with the **xpath:** statement.

   See the **group:** statement to include text from sub-elements.
-  **cmd: constant**

   For ``csv2xml.py`` and ``update_from_csv.py``, create an element
   from the **value:** statement of this document without reference to the CSV file.
   You may also use **constant** in ``xml2csv.py`` but you must include an **xpath:**
   statement with a value that is used for the heading if no **title:** statement
   is specified. The value is inserted unconditionally into the xpath’s text.
-  **cmd: copy**

   For ``xml2csv.py``. If the CSV file specified by the ``--include`` argument contains
   columns in addition to the one with heading "Serial", these columns can be copied
   to the output CSV file. For example::

      cmd: copy
      copy_column: Old Location
      title: Old Loc

   For the accession number specified, copy the value of the column with heading "Old Location"
   in the file specified by ``--include`` to the output CSV file in the column with heading "Old Loc".
   Do not include an **xpath:** statement.
-  **cmd: count**

   Displays the number of occurrences of an element under its
   parent.
-  **cmd: delete**

   For ``update_from_csv.py``. Delete the first element specified by the
   **xpath** statement. If the **delete** command is
   specified, the **xpath:**  and **parent_path:** statements are required and
   the only ones allowed.

   To delete complete ``Object`` elements, use ``filter_xml.py``.
-  **cmd: delete_all**

   Like **delete** except all occurrences of the element are deleted.
-  **cmd: items**
   Used by ``csv2xml.py`` to create *Item* elements for the multiple
   text strings delimited by the delimiter specified by the **multiple_delimiter:**
   statement.
-  **cmd: keyword**

   Used by ``xml2csv.py`` Find the element specified by the xpath statement
   whose text equals the text in the **value** statement and then return the
   first *Keyword* sub-element's text. This for the special (and deprecated) case where
   an element contains both text and subelements.
-  **cmd: location**

   Update the location of objects. Do not include an **xpath:** statement; the paths
   to be updated are hard-coded. See :ref:`location_command_statements` above for the relevant
   location-command statements.
   Also see :ref:`updating_locations` in the documentation for ``update_from_csv.py``.
   At most one **location** command may be included in a configuration.
-  **cmd: multiple**

   Used by ``xml2csv.py``. Like the **column** command except it produces a
   delimiter-separated list of values. See the optional **multiple_delimiter:** statement.
-  **cmd: reproduction**

   Used by ``csv2xml.py``. A special-purpose command to create a ``Reproduction``
   element group with the accession number followed by ".jpg" as filename. This
   is the name of the file that Modes will use as a thumbnail::

      <Reproduction>
         <Filename>LDHRM.2023.20.jpg</Filename>
      </Reproduction>


Control Commands
++++++++++++++++

These commands do not generate output columns. The **if...** commands are used
by ``xml2csv.py`` and others that read from the XML file to select which
records to output. Multiple **if...** commands may be used; these are
processed in succession and have an **and** relationship, meaning that all of
the tests must succeed for a record to be selected. Note that tests are
case insensitive unless a **case_sensitive** statement is specified in the
control command document.

-  **cmd: global**

   This document contains statements that affect the
   overall processing, not just a specific column. See the section above *Global-command
   Statements*.
-  **cmd: if**

   Selects an object to display if the element text is populated.
-  **cmd: ifnot**

   Selects an object to display if the element doesn’t exist or the
   text is not populated.
-  **cmd: ifattrib**

   Selects an object if the attribute is present and the value is
   populated. Requires an **attribute:** statement.
-  **cmd: ifattribeq**

   Like **ifeq** except compares the value against an
   attribute. Example::

       cmd: ifattribeq
       xpath: .
       attribute: elementtype
       value: fine art
       ---

   This examines the ``elementtype`` attribute on the *Object* element.
-  **cmd: ifattribnoteq**

   Like **ifnoteq** except compares the value against an
   attribute.
-  **cmd: ifcontains**

   Select an object if the value in the **value:**
   statement is contained in the element text.
-  **cmd: ifelt**

   Select an object if the element exists, even if the text is empty.
   If the **required:** statement is included, a warning message is issued.
-  **cmd: ifnotelt**

   Select an object if the element doesn’t exist.
-  **cmd: ifeq**

   Select an object if the element text equals the **value:**
   statement text. Returns false if the element doesn’t exist.
-  **cmd: ifnoteq**

   Select an object if the element text does not equal the
   **value:** statement text.
-  **cmd: ifanyeq**

   This is for elements that can occur more than once but is otherwise like
   **ifeq**.
-  **cmd: ifnotanyeq**

   This is for elements that can occur more than once but is otherwise like
   **ifnoteq**. The object is selected if none of the instances of this element
   equals the contents of the **value:** statement.
-  **cmd: ifexhib**

   A special purpose command that selects an object if it was displayed at a
   particular exhibition. The exhibition number (from ``exhibition_list.py``)
   must be specified in the **value** statement.  This assumes that Exhibition
   elements exist as follows, with subelement text exactly matching the values
   in ``exhibition_list.py``::

      <Exhibition>
         <ExhibitionName>The Art of William Heath Robinson</ExhibitionName>
         <CatalogueNumber>115</CatalogueNumber>
         <Place>Dulwich Picture Gallery</Place>
         <Date>
            <DateBegin>3.11.2003</DateBegin>
            <DateEnd>18.1.2004</DateEnd>
         </Date>
      </Exhibition>

- **cmd: ifnoexhib**

   Select objects that have never been exhibited. No **xpath:** or other statement
   is required. This assumes the normal format as described above.
-  **cmd: ifcolumneq**

   Used in ``csv2xml.py``. Process this row in the CSV file if the value in the
   column named in this document’s **title** statement is equal the value named
   in this document’s **value:** statement.

The **global** Command
++++++++++++++++++++++

-  **cmd: global**

   This document contains statements that affect the
   overall processing, not just a specific column. See the section above *Global-command
   Statements*. Some of the statements affect the entire process, like **delimiter:**.
   Some of the statements affect the individual columns in the associated CSV file and
   may be overriden by the same named statement in individual documents.

