#
INFILE=/Users/mlg/pyprj/hrm/scans/letters_index_reformed.csv
# -------------------------------
#
#   Select only rows with Type == "letter"
#
# goawk -i 'csv header'  \
# 'BEGIN  {print "Serial,Multiple Images,Date,From,To,Type,Description,Comment"
#          OUTPUTMODE = "csv"}
#         { type = @"Type"
#           gsub(/ /, "", type)
#           if (type == "letter") print
#         }# ' $INFILE >tmp/letters_only.csv
#
# -------------------------------
#
# List unique values of Type
#
# goawk -i 'csv header'  \
# 'BEGIN  {print "Serial,Multiple Images,Date,From,To,Type,Description,Comment"
#          OUTPUTMODE = "csv"}
#         {$type = @"Type"
#          gsub(/ /, "", $type)
#          print $type}
# ' $INFILE | sort |uniq
#          #print }
#
# -------------------------------
#
# goawk -i 'csv header'  \
# 'BEGIN  {print "Serial,Multiple Images,Date,From,To,Type,Description,Comment"
#          OUTPUTMODE = "csv"}
#         @"Type" != "letter" {print}
# ' $INFILE > tmp/notletter.csv
#
# -------------------------------
#
# Print rows with empty Type fields
#
# goawk -i 'csv header'  \
# '        { type = @"Type"
#           gsub(/ /, "", type)
#           if (type == "") print
#         }
# ' $INFILE
#
# -------------------------------
#
# goawk -i csv -H '
# {h = FIELDS[1]
#  for (i=2; i in FIELDS; i++) h = h ","  FIELDS[i]
#  print h
#  exit }
# ' $INFILE >tmp/letters_only.csv
#
# -------------------------------
#
# goawk -i csv -H -o csv \
# '
#         @"Type" == "letter" {print}
# ' $INFILE >>tmp/letters_only.csv
#
# -------------------------------
#
#
# Find "Type" values with leading/trailing spaces
#
# goawk -i 'csv header'  \
# '        { type = @"Type"
#           orgtype = type
#           gsub(/ /, "", type)
#           if (orgtype != type) print @"Serial" " org: [" orgtype "] type " type
#           # if (type == "letter") print
#         }
# ' $INFILE
#
# -------------------------------
#
# Print rows with empty Type fields
#
# goawk -i 'csv header'  \
# '        { type = @"Type"
#           gsub(/ /, "", type)
#           if (type == "") print
#         }
# ' $INFILE
#
# -------------------------------
#
# Count Type values
#
# goawk -i 'csv header'  \
# '        {$type = @"Type"
#           gsub(/ /, "", $type)
#           b[$type]++}
# END {for (i in b) print i, b[i]+0}
# ' $INFILE |sort
# -------------------------------
#
#   Select only rows with Type == "letter"
#
goawk -i csv -H  \
'BEGIN  {print "Serial,Multiple Images,Date,From,To,Type,Description,Comment"
         OUTPUTMODE = "csv"}
        { type = @"Type"
          gsub(/ /, "", type)
          if (type == "letter") print
        }' $INFILE >tmp/letters_only.csv
