# USBKEY=HP_USB_FD
# find ../collection/aawebimgs -name '*.jpg' -exec cp '{}' /Volumes/$USBKEY/harvest \;
# for f in /Volumes/$USBKEY/harvest/*.jpg; do mv "$f" "${f/collection_/}"; done
SOURCE=/Users/mlg/Library/Mobile\ Documents/com~apple~CloudDocs/hrm_downloads/2023-10-22_high_res_images
DEST=/Volumes/Transcend/2023-10-22_high_res_images
for dir in imgsrc/*
do
    # echo dir= $dir
    # if [[ -d $dir ]]
    #    then
            # for file in $dir/*
            # do
    cp $dir/* $DEST
            # done
    # fi
done
