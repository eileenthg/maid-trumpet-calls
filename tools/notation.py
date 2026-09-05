"""Tiny editable notation: 'C5:1.25 F5:1.25 G5:.75 R:0.5' — duration in BEATS, R = rest."""
NN={'C':0,'C#':1,'DB':1,'D':2,'D#':3,'EB':3,'E':4,'F':5,'F#':6,'GB':6,
    'G':7,'G#':8,'AB':8,'A':9,'A#':10,'BB':10,'B':11}
def midi(tok):
    t=tok.upper().replace('♭','B').replace('♯','#')
    i=len(t)-1
    while i>0 and (t[i].isdigit() or t[i]=='-'): i-=1
    name,octv=t[:i+1],int(t[i+1:])
    return NN[name]+(octv+1)*12
def parse(s, bpm, gate=1.0):
    beat=60.0/bpm; seq=[]; t=0.0
    for tok in s.split():
        n,_,d=tok.partition(':'); dur=float(d or 1)*beat
        if n.upper()!='R': seq.append([t, dur*gate, midi(n)])
        t+=dur
    return seq
def dump(seq, bpm):
    beat=60.0/bpm; NAMES=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
    return ' '.join('%s%d:%g'%(NAMES[m%12], m//12-1, round(d/beat,4)) for _,d,m in seq)
