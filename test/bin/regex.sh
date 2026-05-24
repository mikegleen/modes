#!/bin/bash
path=/Users/mlg/pyprj/hrm/modes/prod_update/normal/2026-03-17d_line.xml
if [[ "$path" =~ ^.+/(.+)\.xml$ ]]; then
    echo ${BASH_REMATCH[1]}
else
    echo nah
fi
