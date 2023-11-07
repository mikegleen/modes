goawk -i 'csv header' 'BEGIN{print "Serial,hxw"}
                    {if (! $3)
                        print @"Serial"
                     else
                        printf "%s,%s x %s mm\n", @"Serial", @"height", @"width"}' $1
