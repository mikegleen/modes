Modes Python Library
====================

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
documents, separated by lines containing “---” in the left three columns.
Each document roughly corresponds to a column to write to the CSV file.
Each document contains some of the following statements. Statements are
case sensitive; all must be lower case. Commands can be
column-generating or control statements.

Statements
~~~~~~~~~~

-  **cmd** Required. See below for a description of the individual
   commands.
-  **xpath** Required. This describes the XSLT path to a relevant XML
   element.
-  **attribute** Required by the **attrib** and **ifattrib** commands.
-  **title** Optional. If omitted, a best-guess title will be created
   from the xpath statement. If in a control document, this will be
   shown in diagnostics.
-  **value** Required for **ifeq** or **ifattrib** or **ifcontains**
   command.
-  **normalize** Adjust this ID number so that it sorts in numeric
   order.
-  **casesensitive** By default, comparisons are case insensitive.
-  **width** truncate this column to this number of characters
-  **required** Issue an error message if this field is missing or
   empty. Valid only with a control command (**if** ...).
-  **delimiter\*\*** The character to use for the CSV file field
   separator. The default is “,”.
-  **record_tag\*\*** This is the tag (of which there are usually many)
   that will be the root for extracting columns. The default is
   ‘Object’.
-  **record_id_xpath\*\*** This is where the ID is found based on the
   root tag. The default is ‘./ObjectIdentity/Number’. In addition to
   being output as column 1 by default, the ID is used in error
   messages.
-  **skip_number\*\*** Do not automatically write the ID number as the
   first column. This can be useful when sorting on another column. The
   ID number can be manually inserted as another column.

Commands
~~~~~~~~

Each document has one **cmd** statement, which is usually the first
statement in the document.

-  **attrib** Like **column** except displays the value of the attribute
   named in the **attribute** statement.
-  **column** This is the basic command to display the text of an
   element.
-  **count** Displays the number of occurrences of an element under its
   parent.
-  **global\*** This document contains statements that affect the
   overall output, not just a specific column.
-  **if\*** Control command that selects an object to display if the
   element text is populated.
-  **ifattrib\*** Like **if** except tests for an attribute
-  **ifattribeq\*** Like **ifeq** except compares the value against an
   attribute
-  **ifcontains\*** Select an object if the value in the **value**
   statement is contained in the element text.
-  **ifeq\*** Select an object if the element text equals the **value**
   statement text.

 | \* These commands do not generate output columns.
 | \*\* These statements
   are only valid if the command is **global**. ## xml2csv.py Extract
   fields from an XML file, creating a CSV file with the fields as
   specified in the configuration. ## location.py Do updating, listing and
   validating of object locations. If updating a current location, a
   previous location element is created.
