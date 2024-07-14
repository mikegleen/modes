update_from_csv
===============

.. automodule:: update_from_csv

*The help text when executing the program with the ``-h`` option follows:*


.. argparse::
   :filename: ../src/update_from_csv.py
   :func: getparser
   :prog: update_from_csv.py

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
   **add_mda_code** forces ``LDHRM.`` to be prepended to the given number.
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
``Type=`` clause in the xpath, but it is included to avoid confusion. The **child** and
**child_value** statements in this document will create the subelement with tag *Type*
and text ``Adopt a Picture``. The **value** statement is mandatory with a **constant**
command but is left empty resulting in no text in the *Association* element. The text
will appear in the child element, *Type*.

Command # 2 creates a *Person* element with no text. Command # 3 creates a *PersonName*
subelement to the newly created *Person* element containing text from the ``Name`` column
in the CSV file. The **person_name** statement causes the name to be converted to
"lastname, firstname" format.

Commands # 4, 5, and 6 similarly create *SummaryText/Keyword* and *SummaryText/Note*
elements. Command # 6 contains the **element:** statement to designate the subelement
name to be created. If it was not specified, then the element would be *Dedication* taken
from the **title:** statment. The **title:** is ``Dedication`` because that is the heading
of the corresponding column in the CSV file.

Command # 7 creates a *Date* subelement. The **date:** statement says to convert the
date to standard Modes format of dd.mm.yyyy.

The shell command to effect this update is::

    python src/update_from_csv. \
      prod_update/normal/2022-10-31_loc_JB010.xml \
      prod_update/normal/2022-11-01_adopt.xml \
      -c src/cfg/y010_adopt_a_picture.yml \
      -m results/csv/sally/pictures_adopted.csv \
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

The first command, **global**, contains the **add_mda_code** statement, required because the
given serial numbers were missing the leading ``LDHRM`` prefix.

Command # 2 creates the initial *References* group. The **value** statement is
required but is left empty. Note that the **insert_after** statement contains
a simple tag name, not an XPATH.

Command # 3 creates the *Reference* element with the
attribute ``elementtype="First Published In"``.

Commands # 4 and 5 create the sub-elements containing the actual data from the
CSV file. In #4, the **title** statement indicates the CSV file column to fetch
the data from and the **element** statement indicates the name of the element to
create. This is required as it would otherwise be "Story", taken from the **title**
statement.


Inserting Sub-IDs
~~~~~~~~~~~~~~~~~

.. note::
   This feature is separate from the **item** command used in ``csv2xml.py``.
   That command is used to extract a list of items from a single cell in a
   row while this process creates one item from each row.

This is a special mode in ``update_from_csv.py`` wherein all of the rows in the
input CSV file contain serial numbers which specify sub-IDs. Examples are::

   JB1204.10
   LDHRM.2022.10.4

In each case there is an extra field at the end of the ID. This field must be
numeric. This mode is enabled by the global statement **subid_parent** which
must contain the path to the parent element of the Item elements to be inserted
for the new subIDs. You must also specify **subid_grandparent** for the case
of the parent not existing.

A sample YAML configuration file is::

   cmd: global
   subid_parent: ItemList
   subid_grandparent: .
   ---
   cmd: column
   xpath: Date
   ---
   cmd: column
   xpath: BriefDescription
   title: Description

Note that the XPATH is relative to the subid_parent. The subid_parent is relative
to the subid_grandparent which must be an absolute path.

The corresponding CSV file is::

   Serial,Date,Description
   L7.1,13.12.1940,"From: Jack Sprat, To: Joe Blow"
   L7.2,14.12.1940,"From: Jack Sprat, To: Joe Blogs"

This results in the following being inserted in the Object element::

        <ItemList>
            <Item>
                <ListNumber>1</ListNumber>
                <Date>13.12.1940</Date>
                <BriefDescription>From: Jack Sprat, To: Joe Blow</BriefDescription>
            </Item>
            <Item>
                <ListNumber>2</ListNumber>
                <Date>14.12.1940</Date>
                <BriefDescription>From: Jack Sprat, To: Joe Blogs</BriefDescription>
            </Item>
                <BriefDescription>From: Jack Sprat, To: Joe Blogssuper</BriefDescription>
            </Item>
        </ItemList>

Note that the accession number has been expanded from L7 to L007 in accordance
with the rule for "JB" and "L" numbers.
