# labelled contact sheet of decoded frames.
# usage: sheet.py out.jpg START END STEP COLS CELLW
import os, sys, glob
from PIL import Image, ImageDraw
FPS = float(os.environ.get('FPS', 30))        # frame rate of the reference
FRAMES = os.environ.get('FRAMES', 'frames')   # folder holding f%04d.jpg

out=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3]); st=int(sys.argv[4]); cols=int(sys.argv[5]); cw=int(sys.argv[6])
idx=list(range(a,b+1,st))
w0,h0=Image.open(sorted(glob.glob(os.path.join(FRAMES,'f*.jpg')))[0]).size
ch=int(cw*h0/w0)          # cells keep the reference's aspect, portrait or landscape
rows=(len(idx)+cols-1)//cols
pad=22
W=cols*cw; H=rows*(ch+pad)
sh=Image.new('RGB',(W,H),(20,20,20))
d=ImageDraw.Draw(sh)
for n,fi in enumerate(idx):
    p=os.path.join(FRAMES,'f%04d.jpg'%fi)
    if not os.path.exists(p): continue
    im=Image.open(p).resize((cw,ch))
    r,c=divmod(n,cols)
    x=c*cw; y=r*(ch+pad)
    sh.paste(im,(x,y+pad))
    d.text((x+4,y+5),'f%d  %.2fs'%(fi,(fi-1)/FPS),fill=(255,220,80))
sh.save(out,quality=88)
print(out, sh.size, len(idx),'frames')
