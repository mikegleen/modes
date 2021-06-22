# Modes Python Library
This library provides for manipulation of the XML files exported
from and imported into the *Modes* Museum database system. The
source files contains many special-purpose programs that apply
only to the Heath Robinson Museum database. However, there are
several general-purpose programs that will be documented here.

## The Configuration Domain Specific Language (DSL)
A configuration language is defined in YAML syntax that provides
specification of XML fields and control over whether records
are selected for processing.

The configuration consists of a YAML file broken into multiple documents,
separated by lines containing "---" in the left three columns.
Each document roughly corresponds to a column to write to the CSV file.
Each document
contains some of the following statements. Statements are case sensitive; all
must be lower case. Commands can be column-generating or control statements.

### Statements
+ __cmd__            Required. See below for a description of the individual commands.
+ __xpath__          Required. This describes the XSLT path to a relevant XML element.
+ __attribute__      Required by the __*attrib*__ and __*ifattrib*__ commands.
+ __title__          Optional. If omitted, a best-guess title will be created from the xpath
                    statement. If in a control document, this will be shown in diagnostics.
+ __value__          Required for __*ifeq*__ or __*ifattrib*__ or __*ifcontains*__ command.
+ __normalize__      Adjust this ID number so that it sorts in numeric order.
+ __casesensitive__  By default, comparisons are case insensitive.
+ __width__          truncate this column to this number of characters
+ __required__       Issue an error message if this field is missing or empty. Valid only on a control command (if...).
+ __delimiter**__    The character to use for the CSV file field separator. The
               default is ",".
+ __record_tag**__   This is the tag (of which there are usually many) that will be
               the root for extracting columns. The default is 'Object'.
+ __record_id_xpath**__    This is where the ID is found based on the root tag. The
               default is './ObjectIdentity/Number'. In addition to being
               output as column 1 by default, the ID is used in error messages.
+ __skip_number**__  Do not automatically write the ID number as the first column. This can be useful when
               sorting on another column. The ID number can be manually inserted as another
               column.

### Commands
Each document has one __*cmd*__ statement, which is usually the first statement in
the document.

+ __attrib__        Like __*column*__ except displays the value of the attribute named in the __*attribute*__ statement.
+ __column__        This is the basic command to display the text of an element.
+ __count__         Displays the number of occurrences of an element under its parent.
+ __global\*__       This document contains statements that affect the overall output, not just a specific column.
+ __if\*__           Control command that selects an object to display if the element text is populated.
+ __ifattrib\*__     Like __*if*__ except tests for an attribute
+ __ifattribeq\*__   Like __*ifeq*__ except compares the value against an attribute
+ __ifcontains\*__   Select an object if the value in the __*value*__ statement is contained in the element text.
+ __ifeq\*__         Select an object if the element text equals the __*value*__ statement text.

\*  These commands do not generate output columns.<br>
\*\* These statements are only valid if the command is __*global*__.
## xml2csv.py
Extract fields from an XML file, creating a CSV file with the
fields as specified in the configuration.
## location.py
Do updating, listing and validating of object locations. If updating
a current location, a previous location element is created.
