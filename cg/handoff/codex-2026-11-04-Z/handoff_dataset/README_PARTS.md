# NAUS handoff_dataset — split upload

Each part is an independent zip; extract all into the same directory to rebuild `handoff_dataset/`.

- part1: top-level docs (README/SPEC/LAYOUT_FACTS/MODEL_SOURCES/TASK_PROMPTS), calib/, code/, images/ (+ this README)
- part2: images_3000/, models/eclipse65/
- part3: models/beolab28_obj/ (B&O BeoLab 28 OBJ)
- part4: models/original_zip/ (original beolab28.zip)

Rebuild:
    mkdir work && cd work
    for f in ../NAUS_handoff_part*.zip; do python3 -m zipfile -e "$f" .; done   # or: unzip -o each
Result: ./handoff_dataset/...
