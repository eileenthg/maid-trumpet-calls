import os, json, numpy as np
SR=44100
_here=os.path.dirname(os.path.abspath(__file__))
Z=json.load(open(os.path.join(_here,'zunpet_zones.json')))
D=np.load(os.path.join(_here,'zunpet.npz'))

def _zone(note):
    for z in Z:
        if z['lo']<=note<=z['hi']: return z
    return Z[-1]

def play(note, dur, vel=1.0, atk=0.010, rel=0.09):
    z=_zone(int(note)); a=D[z['name']]
    ls=z['loops']-z['start']; le=z['loope']-z['start']
    has=0<=ls<le<=len(a)
    r=2**((note-z['root']+z['corr']/100.0)/12.0)*(z['sr']/SR)
    N=int((dur+rel)*SR); out=np.zeros(N); pos=0.0
    for i in range(N):
        if pos>=len(a)-2:
            if has: pos=ls+(pos-le)%(le-ls)
            else: break
        i0=int(pos); fr=pos-i0
        out[i]=a[i0]*(1-fr)+a[i0+1]*fr
        pos+=r
        if has and pos>=le: pos-=(le-ls)
    k=max(1,int(atk*SR)); out[:k]*=np.linspace(0,1,k)
    q=max(1,int(rel*SR)); out[-q:]*=np.linspace(1,0,q)**1.5
    return out*vel

def render(notes, t0=0.0, pad=0.30, vel=0.95):
    """notes: list of (start, dur, midi) absolute seconds."""
    if not notes: return np.zeros(int(0.1*SR))
    end=max(s+d for s,d,_ in notes)-t0
    buf=np.zeros(int((end+pad)*SR)+SR//10)
    for st,du,m in notes:
        s=play(int(m), du, vel); i=int((st-t0)*SR)
        if i<0: continue
        j=min(len(buf), i+len(s)); buf[i:j]+=s[:j-i]
    return buf

def finalize(buf, path, peak_db=-1.0, fade=0.010):
    b=np.trim_zeros(np.asarray(buf,dtype=np.float64),'b')
    if len(b)==0: return 0.0
    k=max(1,int(fade*SR)); b=b.copy(); b[-k:]*=np.linspace(1,0,k)
    pk=np.abs(b).max()
    if pk>0: b*=(10**(peak_db/20))/pk
    import soundfile as sf
    sf.write(path, b.astype(np.float32), SR, format='OGG', subtype='VORBIS')
    return len(b)/SR
