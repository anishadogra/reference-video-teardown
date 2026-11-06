# per-frame colour-mask count + bbox. edit BAND/masks for the clip.
import os
FPS = float(os.environ.get('FPS', 30))      # frame rate of the reference
FRAMES = os.environ.get('FRAMES', 'frames')   # folder holding f%04d.jpg
import glob
import numpy as np
from PIL import Image
# rows of the actual picture inside the frame: BAND="y0,y1" (crop away letterbox or UI)
BAND=tuple(int(v) for v in os.environ.get('BAND','100,370').split(','))
fs=sorted(glob.glob(os.path.join(FRAMES,'f*.jpg')))
print("   f      t    GRN    RED |  gx0  gx1  gy0  gy1  rx0  rx1  ry0  ry1   (-1 = colour not present)")
for i,f in enumerate(fs):
    a=np.array(Image.open(f).convert('RGB')).astype(int)[BAND[0]:BAND[1]]
    r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    gm=(g>90)&(g-r>35)&(g-b>35)
    rm=(r>110)&(r-g>55)&(r-b>55)      # NB: also catches skin -- read the baseline
    out=[i+1, i/FPS, int(gm.sum()), int(rm.sum())]
    for m in (gm,rm):
        ys,xs=np.where(m)
        out += [int(xs.min()),int(xs.max()),int(ys.min()),int(ys.max())] if m.sum()>40 else [-1,-1,-1,-1]
    print(("%4d %6.2f %6d %6d | " % tuple(out[:4])) + " ".join("%4d"%v for v in out[4:]))
