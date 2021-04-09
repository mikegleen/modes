awk '/<\/DateBegin>/{sub(/\s*<DateBegin>/, "");sub(/<\/DateBegin>/, "");print}' results/xml/pretty/2021-03-28_fix402_pretty.xml >tmp/datebegin.csv

