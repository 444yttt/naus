"""blender -b -P exr2npy.py -- in.exr out.npy : dump an EXR (combined RGBA, top row first) to numpy float32."""
import bpy, sys, numpy as np
a = sys.argv[sys.argv.index('--') + 1:]
im = bpy.data.images.load(a[0]); im.colorspace_settings.name = 'Non-Color'
w, h = im.size; px = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(px)
np.save(a[1], px.reshape(h, w, 4)[::-1])
