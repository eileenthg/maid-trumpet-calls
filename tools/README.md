# tools

How the eight trumpet calls were made, and how to change them.

Everything here is pure `numpy` / `scipy` / `soundfile`:

    pip install numpy scipy soundfile

`soundfile` bundles libsndfile, which reads MP3 and writes OGG Vorbis, so no
ffmpeg is needed.

## Regenerating the sounds

The ZUNpet samples are not committed - they are extracted from a soundfont you
supply, so this repo doesn't redistribute someone else's instrument.

    python extract_zunpet.py "TOUHOU INSTRUMENT + DRUM KIT.sf2"
    python build_sounds.py

That writes `trumpet_0.ogg` .. `trumpet_7.ogg` straight into
`../src/main/resources/assets/tlmtrumpet/sounds/trumpet/`.

## Changing a melody

Edit the notation strings in `build_sounds.py` and re-run it. The format is
`NOTE+OCTAVE:BEATS`, space separated, with `R:n` for a rest:

    C5:1 F5:1 G5:0.5 F5:0.5 C5:0.5 F5:0.5 G5:1.5 Ab5:0.5 Ab5:2

Flats and sharps both parse, so `Ab5` and `G#5` are the same note.

To add another bundled call: append an entry to `SET` here, add its name to
`BUILT_IN_CALLS` in `TlmTrumpet.java`, add an `item.trumpet.<name>` block to
`sounds.json`, and add `data/tlmtrumpet/tlmtrumpet/trumpet_call/<name>.json`
pointing at it. The name is the same in all four places.

If you only want to add a call for your own world or modpack, you do not need
to touch this mod at all - use a datapack plus a resource pack instead. See the
main [README](../README.md#adding-your-own-calls-with-a-datapack).

## The files

| | |
|---|---|
| `notation.py` | the mini notation parser |
| `zunpet.py` | sampler - pitch-shifts a zone, sustains on its loop points, applies an envelope |
| `fx.py` | convolution reverb from a synthetic decaying-noise impulse response |
| `extract_zunpet.py` | pulls multisamples out of an SF2 (a RIFF container) |
| `build_sounds.py` | the eight final melodies, and the render pipeline |
| `transcribe.py` | melody transcriber, used to lift the tunes off the source MP3s |

## About `transcribe.py`

This is what produced the first drafts of the melodies. It cleans the audio
(harmonic/percussive separation, then a high-pass to drop kick and bass), scores
candidate pitches by harmonic summation, picks a smooth path through them with a
Viterbi decode, and quantises the result to the track's own beat grid.

It gets you close, not exact. Two known limits, both hit during this project:

- **Repeated notes merge.** `segment()` groups consecutive frames of the same
  pitch, so a re-articulated G-G becomes one long G. Onset detection can catch
  this on sparse material but not on dense mixes where percussion fires on every
  16th.
- **Octave errors on short notes.** Harmonic summation is biased toward
  sub-octaves, so brief notes can land an octave low.

Both were fixed by ear, which is why the notation in `build_sounds.py` is the
source of truth rather than anything this script outputs.
