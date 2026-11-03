# Fetch the CC0 oak textures used by furniture.py
for m in diff_2k rough_2k nor_gl_2k; do curl -sS -o "$(dirname "$0")/oak_$m.jpg" "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/oak_veneer_01/oak_veneer_01_$m.jpg"; done
