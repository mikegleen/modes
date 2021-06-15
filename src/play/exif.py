from PIL import Image
from PIL.ExifTags import TAGS

iname = '/Volumes/Transcend/Downloads/hrmalt/accessioned_medium_res/JB006.jpg'
img = Image.open(iname)
exifdata=img.getexif()

for tag_id in exifdata:
     # get the tag name, instead of human unreadable tag id
     tag = TAGS.get(tag_id, tag_id)
     data = exifdata.get(tag_id)
     # decode bytes
     if isinstance(data, bytes):
         data = data.decode()
     print(f"{tag_id:04X},{tag:25}: {data}")

