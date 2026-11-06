# scripts

All take frames already decoded to `frames/f%04d.jpg` (half res is fine). Run them from the
job folder. Two environment variables apply to every frame script: `FRAMES` (folder, default
`frames`) and `FPS` (default 30).

    mkdir -p frames
    ffmpeg -y -v error -i INPUT -vf scale=iw/2:ih/2 -q:v 3 frames/f%04d.jpg
    ffmpeg -y -v error -i INPUT -ac 1 -ar 16000 aud.wav

- `sheet.py out.jpg START END STEP COLS CELLW` — labelled contact sheet.
- `diff.py` — frame-to-frame difference curve; finds the real cuts.
- `events.py` — per-frame colour-mask pixel count + bbox; graphic open/close frames. Set `BAND="y0,y1"` and edit the masks for the clip.
- `filmstrip.py START END [out.jpg]` — every frame of one crop band, stacked and numbered; exact text in/out. Set `CROP="x0,y0,x1,y1"`.
- `edges.py` — top/bottom edge of the content block every 5th frame; finds hidden scale moves.
- `audio.py [STEP] [WAV]` — RMS envelope, digital-silence detection, zero-crossing rate.

Read `../SKILL.md` for what each one is for and how to interpret it.
