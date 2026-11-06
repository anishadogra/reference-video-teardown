# Reference Video Teardown

Turns a reference video into a frame-by-frame editing breakdown you can actually rebuild from: where the cuts are, how the masks open, which hand movement triggers which reveal, the exact in and out frame of every word on screen, the transitions, the layer stack, the effects, and the timing. It ends with a step-by-step recreation guide and a reusable system prompt for the style. It is an agent skill plus six small Python scripts that measure the decoded frames and the audio, so the numbers in the write-up come from the file and not from a model looking at thumbnails.

By Anisha Dogra, co-founder of [RAAY Creative](https://raaycreative.com). This came out of studio work where a client or a teammate would send a reel and say "make it like this", and the first teardowns read well but described transitions that were not there and missed a slow push-in that ran the whole length of the clip. Corrections and disagreements are welcome — [open an issue](../../issues/new) before opening a pull request.

## The problem

Ask an agent how a reel was edited and it will tell you. Confidently, in detail, with technical terms. A lot of it will be invented.

It watches a handful of sampled frames, sees the picture change between two of them, and calls it a transition. It cannot see a mask opening over four frames because it never looked at those four frames. It cannot see a composite scaling from 1.000 to 1.088 over fourteen seconds, because no single pair of frames differs enough to notice. It reports a sound effect that is actually the speaker's "s". The write-up sounds like an editor's notes, and an editor who tries to build from it finds out on the first pass that half of it is wrong.

The fix is not a better prompt. It is measurement. Decode every frame, compute the difference between neighbours, and the real cuts announce themselves as spikes while everything else turns out to be a mask. Stack the caption band frame by frame and the word timings stop being estimates. Track the edges of the content block and the hidden zoom shows up as a straight line.

## The rules that matter most

**Measure, do not eyeball.** Every number in the breakdown has to come off the decoded frames or the extracted audio. A contact sheet at a few frames per second is for orientation, never for timing.

**Say when you cannot confirm something.** If a detail is not visible enough to be sure, the write-up says "I cannot confirm this from the visible frames." A teardown with honest gaps is useful. A teardown with confident guesses costs a render to find out which parts were guesses.

**Explain how it is edited, not just what happens.** "Text appears" is a description. "Hard-swapped on frame 112, no fade, positioned above the raised hand's bounding box" is something an editor can build.

## What is in here

| | |
|---|---|
| **[SKILL.md](SKILL.md)** | The whole method as a drop-in agent skill: the ten-step measurement pipeline, the eleven-section output format, the write-up rules, and the gotchas that cost time on real references. |
| **[scripts/diff.py](scripts/diff.py)** | Frame-to-frame difference curve. Finds the real cuts. |
| **[scripts/events.py](scripts/events.py)** | Per-frame pixel count and bounding box for each graphic colour. Exact open and close frames, and how a graphic tracks the hands. |
| **[scripts/filmstrip.py](scripts/filmstrip.py)** | Every frame of one crop band stacked and numbered. Exact in and out frames for on-screen text. |
| **[scripts/edges.py](scripts/edges.py)** | Top and bottom edge of the content block over time. Catches slow scale and push-in moves. |
| **[scripts/sheet.py](scripts/sheet.py)** | Labelled contact sheet for orientation. |
| **[scripts/audio.py](scripts/audio.py)** | RMS envelope, digital-silence detection and zero-crossing rate. Separates edits from recordings and stings from music. |

## How to use it

You need `python3`, `ffmpeg`, and the packages in `requirements.txt` (Pillow and numpy; the optional ones are listed there).

    pip install -r requirements.txt

Copy the folder into your agent's skills directory (for Claude Code, `.claude/skills/reference-video-teardown/`) and it loads when someone hands over a reference video and asks how it was made. Or run the scripts yourself:

    mkdir job && cd job && mkdir frames
    ffmpeg -i reference.mp4 -vf scale=iw/2:ih/2 -q:v 3 frames/f%04d.jpg
    ffmpeg -i reference.mp4 -ac 1 -ar 16000 aud.wav
    python3 ../scripts/diff.py
    CROP="0,250,288,320" python3 ../scripts/filmstrip.py 1 120 strip.jpg
    python3 ../scripts/audio.py 0.1

Set `FPS` if the reference is not 30 fps. `events.py` and `filmstrip.py` have bands and colour masks that you set per clip; the defaults suit a half-res portrait reel. [scripts/README.md](scripts/README.md) has the arguments for each one.

## A note on the output

The breakdown format is long on purpose: eleven sections, plus a slot-by-slot template and a list of what could not be confirmed. Sections that do not apply get an explicit "not present in this reference" rather than being dropped, because an empty section tells the editor something was checked, and a missing one does not.
