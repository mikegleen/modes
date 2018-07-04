2017-10-08
----------
Applying the location updates from Stocktake II.
All files in /Users/mlg/pyprj/hrm/modes/ unless noted.

Merge the JB and SH files:
    cat f1 f2 > f3
    manually remove three lines from the middle:
        </Interchange>
        <?xml version="1.0" encoding="windows-1252"?>
        <Interchange>

In: f1 = `results/jb/xml/f_object_8.xml`  
In: f2 = `results/sh/xml/sh-06.xml`  
Out: f3 = `results/xml/f_obj_01.xml`

Execute: src/update_loc2.py  
Update data: stocktake/full_list_by_obj_v3.csv  
In: results/xml/f_obj_01.xml  
Out: results/xml/f_obj_02.xml  

```
Errors:
    Not in CSV file: X9
    Not in CSV file: JB706
    Not in CSV file: JB707
    Not in CSV file: JB708
    In CSV but not XML: JB636
    In CSV but not XML: JB638
    In CSV but not XML: SH288a
```

Adjusted the formatting:

    bin/lintxml.sh results/xml/f_obj_02.xml results/xml/f_obj_03.xml

2017-10-12
----------
Applied fixansi.py
    f_obj_03 -> f_obj_04
Also, f_obj_04a with ASCII encodings.

2017-10-30
----------
Creating f_obj_05 with changes from Geoffrey's email of 25 Oct:

I have just discovered that our latest list has two JB638 entries. Can you please change ‘Bump uncle for bathers’ to JB639.
 
We also need to add ‘A Water-Baby in a jester’s hat’ as JB640. It is located in G4. The medium is pen, ink and watercolour and it was published in Bill the Minder, 1912, page [vi]. The image size is 190 x 78mm.

