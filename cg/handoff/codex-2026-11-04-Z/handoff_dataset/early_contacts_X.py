from pathlib import Path
R=Path(__file__).resolve().parent
code=(R/'photo_inspect_X.py').read_text().replace("for shot in ['u1','u2','p09','p01','p13']:","for shot in ['u2']:").replace("O/'scene_inspection.json'","O/'scene_inspection_u2_early.json'")
exec(compile(code,str(R/'photo_inspect_X.py'),'exec'))
