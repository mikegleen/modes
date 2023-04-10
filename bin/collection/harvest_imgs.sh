USBKEY=HP_USB_FD
# find ../collection/aawebimgs -name '*.jpg' -exec cp '{}' /Volumes/$USBKEY/harvest \;
for f in /Volumes/$USBKEY/harvest/*.jpg; do mv "$f" "${f/collection_/}"; done
