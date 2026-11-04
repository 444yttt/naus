from pathlib import Path
import numpy as np
R=Path(__file__).parent
def objgroups(path):
 groups={};name='default';vertices=[]
 for line in Path(path).read_text(errors='ignore').splitlines():
  if line.startswith(('o ','g ')):name=line[2:]
  elif line.startswith('v '):vertices.append([float(x) for x in line.split()[1:4]])
  elif line.startswith('f '):
   for x in line.split()[1:]:
    idx=int(x.split('/')[0]);groups.setdefault(name,set()).add(idx-1 if idx>0 else len(vertices)+idx)
 return {k:np.asarray([vertices[i] for i in sorted(v)]) for k,v in groups.items()}
def hull(points):
 p=sorted(set((round(float(x),7),round(float(y),7)) for x,y in points))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lower=[];upper=[]
 for q in p:
  while len(lower)>=2 and cross(lower[-2],lower[-1],q)<=0:lower.pop()
  lower.append(q)
 for q in reversed(p):
  while len(upper)>=2 and cross(upper[-2],upper[-1],q)<=0:upper.pop()
  upper.append(q)
 return lower[:-1]+upper[:-1]
if __name__=='__main__':
 for f in ['Oleandro_CS2031/cs2031.obj','Icaro_CS4114/cs4114-r_160.obj']:
  for k,v in objgroups(R/'reference'/f).items():
   if 'Oleandro' in f or ('__open' in k and ('piano_top' in k or 'gambe' in k)):
    print(k,len(v),'min',v.min(axis=0),'max',v.max(axis=0))
