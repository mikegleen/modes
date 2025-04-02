#!/bin/zsh
#
#   Fix the <Exhibition> element group. Convert the Place element to
#   contain a subgroup as Place is a locked element in the DTD.
# 	<Exhibition>
# 		<ExhibitionName>Heath Robinson at War</ExhibitionName>
# 		<Place>Mottisfont Abbey</Place>
# 		<Date>
# 			<DateBegin>20.1.2024</DateBegin>
# 			<DateEnd>14.4.2024</DateEnd>
# 		</Date>
# 	</Exhibition>
# to
# 	<Exhibition>
# 		<ExhibitionName>Heath Robinson at War</ExhibitionName>
# 		<Place>
# 		    <PlaceName>Mottisfont Abbey</PlaceName>
#       </Place>
# 		<Date>
# 			<DateBegin>20.1.2024</DateBegin>
# 			<DateEnd>14.4.2024</DateEnd>
# 		</Date>
# 	</Exhibition>

#
set -e
INXML=2025-03-29_JB1142.xml
SCRIPT=$(python -c "print('$ZSH_ARGZERO'.split('.')[0].split('/')[-1])")
echo SCRIPT: $SCRIPT
OUTXML=$SCRIPT.xml
DELTAXML=${SCRIPT}_delta.xml
#
python src/once/x058_patch_place.py prod_update/normal/$INXML prod_update/normal/$OUTXML
python src/xmldiff.py prod_update/normal/$INXML prod_update/normal/$OUTXML -o prod_delta/normal/$DELTAXML
bin/syncupdate.sh
bin/syncdelta.sh

