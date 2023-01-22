goawk -i 'csv header'  \
'BEGIN  {print "Serial,Title,SummaryText,firstpublishedin"
         OUTPUTMODE = "csv"}
        {
            if (@"SummaryText" ~ /.*p ?[0-9ivx]+$/ ) {
                print
            }
        }
' tmp/report.csv >tmp/pgsn.csv
