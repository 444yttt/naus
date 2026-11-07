from pathlib import Path
R=Path(__file__).resolve().parent
text=(R/'verify_scene_X.py').read_text().replace("for shot in ['u1','u2','p09','p01','p13']:","for shot in ['u1','u2']:").replace("O/'scene_delta_X.json'","O/'scene_delta_early_X.json'")
exec(compile(text,str(R/'verify_scene_X.py'),'exec'))
