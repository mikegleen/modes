#awk 'BEGIN{for(i=1;i<=32;i++) {print "SH68.",i}}'|awk 'BEGIN{print"Serial"}{ gsub (" ", "", $0); print}'>tmp/update.csv
awk 'BEGIN{FS="";for(i=1;i<=32;i++) {print "SH68." i}}'
