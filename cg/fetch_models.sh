#!/bin/sh
# Downloads the manufacturer 3D files used by furniture.py into $1 (default ./models). Not committed: third-party assets.
# Audo files come from Audo's public press site (audo.presscloud.com, no login); LG and Apple publish theirs as
# AR models on their product pages. B&O does not publish 3D publicly, so BeoLab 28 and Beosound Balance are modelled
# in furniture.py from B&O's product sheet dimensions. Androgyne Ø150 and Ready chair zips were supplied by the client.
set -e
M=${1:-models}; mkdir -p "$M/dl" "$M/x" "$M/lg" "$M/homeview"
P=https://presscloud.com/file
for f in 27/276603716357428/Eave_Modular_86_Corner.zip 95/959345778268344/Eave_Modular_86_Open_Section.zip \
         80/808704719339494/Plinth_Tall_3D.zip 86/865079515093038/Plinth_Cubic_3D.zip \
         93/931576266815411/Androgyne_Lounge_Table_3D.zip 78/789390281849948/Carrie_LED_3D.zip; do
  n=$(basename "$f" .zip); curl -sfL -o "$M/dl/$n.zip" "$P/$f"; d="$M/x/$n"; [ "$n" = Carrie_LED_3D ] && d="$M/x/carrie"; unzip -oq "$M/dl/$n.zip" -d "$d"
done
curl -sfL -o "$M/lg/g5_65.glb" https://www.lg.com/content/dam/channel/wcms/global/lg-ar/tv/18_oled65g5rla/oled-g5-oled65g5rla_241216.glb
curl -sfL -o "$M/lg/g5_55.glb" https://www.lg.com/content/dam/channel/wcms/global/lg-ar/tv/13_oled55g5rla/oled-g5-oled55g5rla_241216.glb
curl -sfL -o "$M/homeview/apple-homeview.usdz" https://www.apple.com/105/media/us/apple-homeview/2026/f7ce47a8-10f2-455c-b99f-bf9b85a35cb6/ar/apple-homeview.usdz
