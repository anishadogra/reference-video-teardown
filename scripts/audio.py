# RMS envelope + digital-silence + zero-crossing rate.
# usage: audio.py [STEP_SECONDS] [WAV]   (WAV defaults to aud.wav; mono 16-bit, e.g. 16 kHz)
import sys, wave, struct, math
w=wave.open(sys.argv[2] if len(sys.argv)>2 else 'aud.wav'); n=w.getnframes(); sr=w.getframerate()
d=struct.unpack('<%dh'%n, w.readframes(n))
step=float(sys.argv[1]) if len(sys.argv)>1 else 0.1
def rms(a,b):
    s=d[int(a*sr):int(b*sr)]
    return -300 if not s else 20*math.log10((math.sqrt(sum(x*x for x in s)/len(s))+1e-9)/32768)
def zcr(a,b):
    s=d[int(a*sr):int(b*sr)]
    return 0 if not s else sum(1 for i in range(1,len(s)) if (s[i-1]<0)!=(s[i]<0))/(len(s)/sr)
print("dur %.2f  -- values near -270 dBFS are literal zeros = an EDIT, not a recording"%(n/sr))
print("     t    dBFS   ZCR/s  (~250/s = bass sting, ~3000/s = music or voice)")
t=0.0
while t < n/sr - step:
    print("%6.2f %7.1f %7.0f" % (t, rms(t,t+step), zcr(t,t+step))); t+=step
