import json, numpy as np
S = '/tmp/claude-0/-home-user-naus/93a99187-9df5-51d5-b3db-c42aa0696673/scratchpad/t2/'
cams = json.load(open(S + 'cams.json'))
def cam(v):
    c = json.load(open(S + v + '_calib.json')); C = np.array([*cams[v]['cam'], cams[v]['h']])
    return np.array(c['K']), np.array(c['Rcw']), C
def proj(v, P):
    K, R, C = cam(v); pc = (R @ (np.atleast_2d(P) - C).T).T; uv = (K @ pc.T).T; return uv[:, :2] / uv[:, 2:3]
def ray(v, uv):
    K, R, C = cam(v); d = R.T @ np.linalg.inv(K) @ np.array([uv[0], uv[1], 1.0]); return C, d / np.linalg.norm(d)
def hit_plane(v, uv, axis, val):
    C, d = ray(v, uv); t = (val - C[axis]) / d[axis]; return C + t * d
