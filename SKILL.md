---
name: reference-video-teardown
description: Convert a reference video into a frame-by-frame editing breakdown you can recreate from — masking, hand-triggered reveals, transitions, timing, layers, effects, plus a step-by-step rebuild guide and a reusable system prompt. Use when the user supplies a reference video/reel and asks how it was made, how to copy the style, or for a technical/editing analysis. Triggers: "analyse this reference video", "frame by frame", "how is this edited", "make a breakdown of this reel", "I want to recreate this style".
---

# Reference video teardown

A prompt template for editing analysis, and the measurement pipeline that makes it honest.
This is **deterministic frame analysis of a file already on disk**, for VFX, masking and
motion references. It does not scrape anything and it does not ask a vision model to guess.

## Rule zero — measure, do not eyeball

Every number in the output must come off the decoded frames or the extracted audio.
Thumbnails lie. A contact sheet at 3 fps will make you invent transitions that are not
there and miss a global scale move entirely.

If something is not visible enough to be sure, write **"I cannot confirm this from the
visible frames."** Never guess confidently. This is the difference between a teardown
someone can build from and a plausible-sounding fiction.

## Pipeline

`scripts/` has the tools. They need `ffmpeg` on PATH. If it is not installed, the
`imageio-ffmpeg` pip package ships a binary:
`python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`

All scripts read frames from `frames/f%04d.jpg` (override with `FRAMES=dir`) and assume
30 fps (override with `FPS=25` and so on). Read the real frame rate off the probe.

1. **Probe.** `ffprobe file`, or without ffprobe, `ffmpeg -i file 2>&1 | grep -E "Duration|Stream"`.
2. **Decode every frame** at half res into `frames/f%04d.jpg`. A 14 s clip is about 420 frames; that is cheap and it is the only way to get exact in/out frames.
3. **Difference curve** (`diff.py`) — mean abs frame-to-frame difference. This finds the real cuts. A body with a max of ~6/255 and one spike at 48 means **one cut**, and everything else you thought was a transition is a mask.
4. **Colour-mask tracking** (`events.py`) — per-frame pixel count *and bounding box* for each graphic colour. Gives exact open/close frames and, from the bbox, how the graphic tracks the subject's hands. Watch out: naive red masks catch skin — read the baseline before trusting a spike.
5. **Text filmstrip** (`filmstrip.py`) — crop the caption/type band and stack every single frame with its number. This is how you get exact word in/out frames. Nothing else is as reliable.
6. **Global move** (`edges.py`) — track the top and bottom edge of the content block per frame. This catches slow scale/push-in moves that are invisible by eye. In one reference the whole composite scaled ×1.000 → ×1.088, linear, top-anchored, and it would have been missed entirely without this.
7. **Audio** (`audio.py`) — RMS at 100 ms for the shape, 20 ms around events for exact boundaries. Look for **true digital silence** (values at −270 dBFS = literal zeros = an edit, not a recording). Zero-crossing rate separates a bass sting (~250/s) from music (~3000/s).
8. **Word timestamps** — faster-whisper with `word_timestamps=True` for lyric/VO sync. Whisper's word starts are systematically early by ~0.1–0.3 s; report the on-screen frames as the hard data and whisper's as approximate reference.
9. **Zoom, don't squint.** Crop native-res regions and upscale with LANCZOS before reading them. Most of the real findings (a white matte fringe, a duplicated eye, whether a fill is flat or carries image structure) are only visible zoomed.
10. **Flatness test** decides "solid colour layer" vs "graded copy of the plate": standard deviation of the fill. sd < 2 = flat graphic. sd > 40 = it carries image structure, so it is an exposure/grade push on the footage, not a shape.

## Output format

In this order. Sections that do not apply to the reference get an explicit
"not present in this reference" — do not pad them and do not skip them.

1. Overall style summary (simple words)
2. Timestamp-by-timestamp table: time · frame · what happens · hand/body · mask or transition · graphic movement · technical term · how to recreate
3. Masking breakdown
4. Hand movement breakdown — how the hands drive the edit
5. Web / line / path animation breakdown
6. Transition breakdown
7. Layer structure
8. Effect list — **present** and **confirmed absent**
9. Normal language → technical editing language (the user's own phrasing, in whatever language they use, → editor terms)
10. Step-by-step recreation workflow
11. Reusable system prompt
Plus: a reusable slot-by-slot template, and a "things I could not confirm" section.

## Rules for the write-up

- Do not give a surface-level summary.
- Do not skip micro-movements, transitions between actions, timing, hand movement, masking, or how path visuals are created.
- Do not only describe what is happening — explain how it is likely edited.
- Do not make the answer generic. Treat it as training an editor to recreate the style.

## What a good teardown finds

A typical result, from a 13.87 s masking reel: one cut, five hand-driven mask reveals,
11 hard-swapped lyric words, a hidden linear push-in, and a silence → one-black-frame →
darkened-freeze ending. Most of that was invisible on a casual watch and only showed up in
the difference curve, the filmstrip and the edge tracker.

## Gotchas

- **Never name a helper script after a stdlib module** (`typing.py`, `json.py`, `wave.py`, `types.py`). A `typing.py` in the job folder shadowed the stdlib, numpy/cv2 imports failed with a circular-import error, and the failure only showed on the *next* script. Run every analysis from a clean working directory and `os.chdir()` into the job folder after the imports.
- **`white > 225` is not "white text" on an off-white paper background** (#ECECEC = 236). Use `> 245` for #FDFDFD type, or mask on the panel colour first. The same trap: a "not background" mask picks up graph-paper '+' marks; measure the subject with `luma < 200 & (sat > 30 | luma < 150)`.
- **Landscape references**: `sheet.py` sizes cells from the frame's own aspect, but `diff.py` resizes to a 72x128 portrait thumbnail and `filmstrip.py`/`events.py` default to bands for a 288x512 portrait frame. Set `CROP` and `BAND` for the clip, and pull native frames by index through a sequential `cv2.VideoCapture` decode, never `-ss` (seeking lands on a different frame).
- **ORB + `estimateAffinePartial2D` per frame** finds punch-ins, slow zooms and pans that no eye catches (a 1.31x jump zoom over 5 frames, a 0.82x pull-back over 2.4 s). It reads the dominant layer: on a cutout-over-flat-paper shot that is the subject, on a photo it is the photo.
- **Beat-cut test**: band-pass 40-150 Hz, onset peaks, check the phase `mod 60/BPM` per 20 s segment (stable phase = an uncut bed), then the mean |offset| of every cut to the nearest kick versus the random expectation (period/4). Under 0.06 s means beat-cut; 0.15 s means cued to words.
- **Whoosh vs voice**: HF (4-8 kHz) energy alone lies, sibilants live there. Add a voicing test (max normalised autocorrelation at 2.5-12 ms lag; > 0.5 = voiced) and check the word list. In one reference every "SFX" candidate was a sibilant or the ducked music bed returning after the last word.
