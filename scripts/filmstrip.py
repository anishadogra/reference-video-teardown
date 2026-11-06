# every frame of one crop band, numbered. exact in/out frames for on-screen text.
import os
FPS = float(os.environ.get('FPS', 30))      # frame rate of the reference
FRAMES = os.environ.get('FRAMES', 'frames')   # folder holding f%04d.jpg
import sys
from PIL import Image, ImageDraw
a,b = int(sys.argv[1]), int(sys.argv[2])
# the band to watch, in decoded-frame pixels: CROP="x0,y0,x1,y1" (default suits a 288x512 half-res portrait frame)
CROP=tuple(int(v) for v in os.environ.get('CROP','0,250,288,320').split(','))
out=sys.argv[3] if len(sys.argv)>3 else 'strip.jpg'
cw,ch,cols=200,52,4
idx=list(range(a,b+1)); rows=(len(idx)+cols-1)//cols
sh=Image.new('RGB',(cols*(cw+58), rows*ch),(15,15,15)); d=ImageDraw.Draw(sh)
for n,fi in enumerate(idx):
    im=Image.open(os.path.join(FRAMES,'f%04d.jpg'%fi)).crop(CROP).resize((cw,ch))
    r,c=divmod(n,cols); x=c*(cw+58); y=r*ch
    sh.paste(im,(x+56,y)); d.text((x+4,y+18),'%d %.2f'%(fi,(fi-1)/FPS),fill=(255,215,70))
sh.save(out,quality=90); print(out, sh.size)
