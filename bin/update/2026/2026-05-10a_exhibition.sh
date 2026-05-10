 #!/bin/zsh
 python src/exhibition.py prod_save/normal/2026-05-10s_prod_save_sorted.xml \
    --outfile prod_update/normal/2026-05-10a_exhibition.xml \
    --deltafile prod_delta/normal/2026-05-10a_exhibition.xml \
    --exhibition 44 --patch -v 1
