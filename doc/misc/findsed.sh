find tmp/source -name "*.rst" -exec sed -I .bak 's:../src:/Users/mlg/pyprj/hrm/modes/src:' {} ';'
