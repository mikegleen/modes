# -*- coding: utf-8 -*-
"""
The configuration consists of a YAML file broken into multiple documents,
separated by lines containing "---" in the left three columns. Each document
contains some of the following statements. Statements are case sensitive; all
must be lower case. Commands can be column-generating or control statements.

Statements:
-----------
cmd            Required. See below for a description of the individual commands.
xpath          Required. This describes the XSLT path to a relevant XML element.
attribute      Required by the attrib and ifattrib commands.
title          Optional. If omitted, a best-guess title will be created from the xpath
               statement. If in a control document, this will be shown in diagnostics.
value          Required for keyword or if... commands.
normalize      Adjust this ID number so that it sorts in numeric order.
casesensitive  By default, comparisons are case insensitive.
width          truncate this column to this number of characters
required       Issue an error message if this field is missing or empty.
delimiter**    The character to use for the CSV file field separator. The
               default is ",".
multiple_delimiter  The character to use within a column to separate the
               values when used with the multiple command. The statement may
               appear under the global command or a specific multiple command,
               which takes precedence. The default is "|".
record_tag**   This is the tag (of which there are usually many) that will be
               the root for extracting columns. The default is 'Object'.
record_id_xpath**    This is where the ID is found based on the root tag. The
               default is './ObjectIdentity/Number'. In addition to being
               output as column 1 by default, the ID is used in error messages.
skip_number**  Do not write the ID number as the first column. This can be useful when
               sorting on another column.

Commands:     These commands are the single parameter on the cmd statement.
---------
attrib        Like column except displays the value of the attribute named in
              the attribute statement.
column        This is the basic command to display the text of an element. Only
              the first element is returned if there are more than one.
multiple      Like column except it produces a delimiter-separated list of
              values.
count         Displays the number of occurrences of an element under its parent.
keyword       Find the element specified by the xpath statement whose text
              equals the text in the value statement and then return the
              first Keyword sub-element's text.
global*       This document contains statements that affect the overall output,
              not just a specific column.
if*           Control command that selects an object to display if the element
              text is populated.
ifattrib*     Like if except tests for an attribute
ifattribeq*   Like ifeq except compares the value against an attribute
              Example:
                cmd: ifattribeq
                xpath: .
                attribute: elementtype
                value: fine art
                ---
ifattribnoteq*  Similar to iffattribeq
ifcontains*   Select an object if the value in the value statement is contained
              in the element text.
ifeq*         Select an object if the element text equals the value statement text.

*  These commands do not generate output columns.
** These statements are only valid if the command is "global".

"""
