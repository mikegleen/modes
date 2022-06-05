# awk '/<\/DateBegin>/{sub(/\s*<DateBegin>/, "");sub(/<\/DateBegin>/, "");print}' results/xml/pretty/2021-03-28_fix402_pretty.xml >tmp/datebegin.csv
# awk '/<\/DateBegin>/{sub(/\s*<DateBegin>/, "");sub(/<\/DateBegin>*/, "");gsub(/\t/, "");print}' prod_update/pretty/2022-05-02_merge_pretty.xml  >tmp/datebegin.csv
awk  "$(cat <<'_eof_'
    /<\/DateBegin>/{
        sub(/\s*<DateBegin>/, "")
        sub(/<\/DateBegin>*/, "")
        gsub(/\t/, "")
        print
    }
_eof_
)" prod_update/pretty/2022-05-02_merge_pretty.xml >tmp/datebegin.csv
