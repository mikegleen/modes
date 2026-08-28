# find tmp/source -name "*.rst" -exec sed -I .bak 's:../src:/Users/mlg/pyprj/hrm/modes/src:' {} ';'
find source -name "*.rst" -exec sh -c "sed 's:../src:../../src:' {} >tmp/{} " \;
