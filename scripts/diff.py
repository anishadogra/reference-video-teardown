# frame-to-frame mean abs difference -> finds the real cuts.
import os
FPS = float(os.environ.get('FPS', 30))      # frame rate of the reference
FRAMES = os.environ.get('FRAMES', 'frames')   # folder holding f%04d.jpg
import sys, glob
from PIL import Image, ImageChops, ImageStat
fs=sorted(glob.glob(os.path.join(FRAMES,'f*.jpg'))); prev=None; rows=[]
for i,f in enumerate(fs):
    im=Image.open(f).convert('L').resize((72,128))
    if prev is not None:
        rows.append((i+1, i/FPS, ImageStat.Stat(ImageChops.difference(im,prev)).mean[0]))
    prev=im
mx=max(r[2] for r in rows)
print("max diff %.2f  -- a spike near max = a real cut; a flat low body = one take" % mx)
for n,t,v in rows:
    print(f"{n:4d} {t:6.2f} {v:6.2f} {'#'*int(v/mx*40)}{'  <== CUT' if v>mx*0.35 else ''}")
