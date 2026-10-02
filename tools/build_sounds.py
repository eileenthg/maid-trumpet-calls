"""Render the bundled trumpet calls from notation and write them into the mod's assets.

    python build_sounds.py            # -> ../src/main/resources/assets/tlmtrumpet/sounds/trumpet/
    python build_sounds.py --dry      # no reverb
    python build_sounds.py --out DIR  # somewhere else

Requires zunpet.npz / zunpet_zones.json - run extract_zunpet.py first.

Notation is "NOTE+OCTAVE:BEATS", space separated; R:n is a rest. Both flats and
sharps parse, so Ab5 and G#5 are the same note. Edit a line below and re-run.

Each name here must match a sound event registered in TlmTrumpet.java and an
entry in assets/tlmtrumpet/sounds.json, plus a data file at
data/tlmtrumpet/tlmtrumpet/trumpet_call/<name>.json.
"""
import argparse, os
import fx
import zunpet
from notation import parse

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, '..', 'src', 'main', 'resources',
                           'assets', 'tlmtrumpet', 'sounds', 'trumpet')

b = '\u266d'

# name, notation, bpm
SET = [
    ('flowering_night',
     "B4:.5 G5:.5 F#5:.25 G5:.25 F#5:.25 G5:.25 A5:.5 G5:.5 "
     "F#5:.25 G5:.25 F#5:.25 G5:.25 D5:.25 E5:.5 "
     "B5:.5 A5:.25 B5:.25 A5:.25 B5:.25 D6:.5 B5:.5 A5:.5 B5:1", 152.0),
    ('true_hero_descending',
     f"F5:.5 C6:.5 B{b}5:.5 C6:.5 A{b}5:.5 C6:.5 G5:1 "
     f"G5:.5 A{b}5:.5 G5:.5 A{b}5:.5 G5:1.5 B{b}5:1.5 F5:1.5 E{b}5:1.5", 152.0),
    ('true_hero_chromatic',
     f"F5:.5 C6:.5 B{b}5:.5 C6:.5 A{b}5:.5 C6:.5 G5:1 "
     f"G5:.5 A{b}5:.5 G5:.5 A{b}5:.5 G5:1 B{b}5:1 "
     f"E{b}6:0.5 D6:0.25 D{b}6:0.25 C6:3", 152.0),
    ('minoriko_descending',
     "E4:.5 F#4:.5 A4:.5 B4:1.5 C#5:.5 B4:.5 C#5:.5 E5:.5 "
     "C#5:.5 B4:.5 C#5:.5 F#4:1.5", 155.0),
    ('minoriko_ascending',
     "E4:.5 F#4:.5 A4:.5 B4:1.5 C#5:.5 E5:.5 C#5:.5 B4:.5 C#5:.5 F#5:2.5", 155.0),
    ('history_of_the_moon',
     "C5:1 F5:1 G5:0.5 F5:0.5 C5:0.5 F5:0.5 G5:1.5 Ab5:0.5 Ab5:2", 155.0),
    ('bad_apple_arch',
     f"E{b}5:0.5 F5:0.5 G{b}5:0.5 A{b}5:0.5 B{b}5:1 E{b}6:0.5 D{b}6:0.5 B{b}5:1 E{b}5:1 "
     f"B{b}5:0.5 A{b}5:0.5 G{b}5:0.5 F5:0.5 E{b}5:0.5 F5:0.5 G{b}5:0.5 A{b}5:0.5 B{b}5:1", 152.0),
    ('bad_apple_scalar',
     f"E{b}5:0.5 F5:0.5 G{b}5:0.5 A{b}5:0.5 B{b}5:1 A{b}5:0.5 G{b}5:0.5 F5:0.5 "
     f"E{b}5:0.5 F5:0.5 G{b}5:0.5 F5:0.5 E{b}5:0.5 D5:0.5 F5:0.5", 152.0),
    ('gods_loved_arch',
     "A4:.5 A4:.5 C5:.5 D5:1.5 C5:.25 D5:.25 C5:.5 A4:.5 G4:.5 C5:.5 A4:3", 140.0),
    ('gods_loved_ascending',
     "A4:.5 A4:.5 C5:.5 D5:1.5 C5:.25 D5:.25 F5:.5 E5:.5 D5:.5 C5:.5 D5:3", 140.0),
    ('gods_loved_descending',
     "C5:.25 D5:.25 C5:.5 A4:.5 G4:2.75 C5:.25 D5:.25 C5:.5 G4:.5 F4:3", 140.0),
    ('gods_loved_low',
     "D4:.5 E4:.5 F4:1.5 G4:.5 E4:1.5 D4:.5 D4:3", 140.0),
]

# Small room. Bigger tails smear the 16th-note runs in flowering_night.
REVERB = dict(rt60=0.35, wet=0.20, predelay=0.012, damp_hz=5000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--dry', action='store_true', help='skip the reverb')
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    for name, notation, bpm in SET:
        audio = zunpet.render(parse(notation, bpm), t0=0.0)
        if not a.dry:
            audio = fx.reverb(audio, **REVERB)
        path = os.path.join(out, f'{name}.ogg')
        dur = zunpet.finalize(audio, path)
        print(f'{name + ".ogg":<24} {bpm:5.1f} BPM  {dur:4.2f}s  {os.path.getsize(path):6d} B')
    print(f'\n{len(SET)} files -> {out}')


if __name__ == '__main__':
    main()
