# top/bottom edge of the content block per frame -> finds hidden scale / push-in moves.
import os
FPS = float(os.environ.get('FPS', 30))      # frame rate of the reference
FRAMES = os.environ.get('FRAMES', 'frames')   # folder holding f%04d.jpg
import glob
import numpy as np
from PIL import Image
res=[]
for f in range(1,len(glob.glob(os.path.join(FRAMES,'f*.jpg')))+1,5):
    a=np.array(Image.open(os.path.join(FRAMES,'f%04d.jpg'%f)).convert('L')).astype(float)
    rm=a[:,10:-10].mean(1)
    ys=[y for y in range(a.shape[0]) if rm[y]>14]
    res.append((f, ys[0], ys[-1]) if ys else (f,None,None))
base=[r for r in res if r[1] is not None][0]; h0=base[2]-base[1]
print(" f     t    top  bot  height  scale  dTop")
for f,t_,b_ in res:
    if t_ is None: print("%4d %6.2f   --"%(f,(f-1)/FPS)); continue
    print(f"{f:4d} {(f-1)/FPS:6.2f} {t_:4d} {b_:4d} {b_-t_:6d} {(b_-t_)/h0:6.3f} {t_-base[1]:+4d}")
