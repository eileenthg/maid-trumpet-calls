import numpy as np, soundfile as sf
from scipy import signal, ndimage

NN=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
def nn(m): return f'{NN[int(m)%12]}{int(m)//12-1}'

def hpss_harmonic(y, sr, n=2048, hop=512, t_med=31, f_med=31, power=2.0):
    f,t,Z=signal.stft(y,sr,nperseg=n,noverlap=n-hop)
    S=np.abs(Z); ph=np.angle(Z)
    H=ndimage.median_filter(S,size=(1,t_med)); P=ndimage.median_filter(S,size=(f_med,1))
    m=(H**power)/(H**power+P**power+1e-12)
    _,o=signal.istft(S*m*np.exp(1j*ph),sr,nperseg=n,noverlap=n-hop)
    return o[:len(y)]

def highpass(y,sr,fc,order=4):
    b,a=signal.butter(order,fc/(sr/2),btype='high'); return signal.filtfilt(b,a,y)

def salience(y, sr, lo=55, hi=96, hop=256, nfft=4096, nharm=8):
    """Harmonic-summation salience over candidate F0s (quarter-tone grid)."""
    f,t,Z=signal.stft(y,sr,nperseg=nfft,noverlap=nfft-hop)
    S=np.abs(Z)
    cands=np.arange(lo,hi+0.01,0.5)
    freqs=440.0*2**((cands-69)/12.0)
    sal=np.zeros((len(cands),S.shape[1]))
    w=[1.0,0.85,0.65,0.5,0.4,0.32,0.26,0.2][:nharm]
    binhz=sr/nfft
    for h,wt in enumerate(w, start=1):
        idx=freqs*h/binhz
        i0=np.floor(idx).astype(int); fr=(idx-i0)[:,None]
        ok=(i0>=0)&(i0<S.shape[0]-1)
        c=np.zeros_like(sal)
        c[ok]=S[i0[ok]]*(1-fr[ok])+S[i0[ok]+1]*fr[ok]
        sal+=wt*c
    return cands, t, sal, S

def viterbi(sal, cands, jump_pen=0.55, sil_frac=0.14):
    """Decode a smooth pitch path; state -1 = rest."""
    E=np.log(sal+1e-9)
    E=(E-E.mean(axis=0))/ (E.std(axis=0)+1e-9)
    frame_e=sal.sum(axis=0)
    gate=frame_e < sil_frac*np.median(frame_e)*2.0
    K=len(cands); T=sal.shape[1]
    trans=-jump_pen*np.abs(cands[:,None]-cands[None,:])
    dp=np.full((K,T),-1e18); bp=np.zeros((K,T),dtype=int)
    dp[:,0]=E[:,0]
    for t in range(1,T):
        m=dp[:,t-1][:,None]+trans
        bp[:,t]=np.argmax(m,axis=0)
        dp[:,t]=m[bp[:,t],np.arange(K)]+E[:,t]
    path=np.zeros(T,dtype=int); path[-1]=np.argmax(dp[:,-1])
    for t in range(T-1,0,-1): path[t-1]=bp[path[t],t]
    pitch=cands[path].astype(float)
    pitch[gate]=np.nan
    return pitch

def segment(pitch, t, min_dur=0.055):
    """Quantise to semitones and group into notes."""
    q=np.round(pitch)
    notes=[]; i=0
    while i<len(q):
        if np.isnan(q[i]): i+=1; continue
        j=i
        while j+1<len(q) and not np.isnan(q[j+1]) and abs(q[j+1]-q[i])<0.6: j+=1
        dur=t[j]-t[i]
        if dur>=min_dur: notes.append([float(t[i]), float(dur), int(q[i])])
        i=j+1
    # merge adjacent same-pitch notes separated by a tiny gap
    out=[]
    for nte in notes:
        if out and out[-1][2]==nte[2] and nte[0]-(out[-1][0]+out[-1][1])<0.045:
            out[-1][1]=nte[0]+nte[1]-out[-1][0]
        else: out.append(nte)
    return out

def tempo_grid(y, sr, hop=512):
    f,t,Z=signal.stft(y,sr,nperseg=2048,noverlap=2048-hop); S=np.abs(Z)
    flux=np.maximum(0,np.diff(S,axis=1)).sum(axis=0); flux/=flux.max()+1e-12
    ac=np.correlate(flux-flux.mean(),flux-flux.mean(),'full')[len(flux)-1:]
    lags=np.arange(len(ac))/(sr/hop); m=(lags>0.25)&(lags<1.2)
    beat=lags[m][np.argmax(ac[m])]
    best,bs=0,-1
    for off in np.arange(0,beat,0.01):
        idx=((np.arange(off,len(y)/sr-beat,beat))*(sr/hop)).astype(int)
        idx=idx[idx<len(flux)]
        if len(idx)==0: continue
        sc=flux[idx].mean()
        if sc>bs: bs,best=sc,off
    return beat,best

def quantise(notes, beat, off, div=4):
    """Snap note starts/ends to a 1/div-of-a-beat grid."""
    step=beat/div; out=[]
    for st,du,m in notes:
        a=round((st-off)/step)*step+off
        b=round((st+du-off)/step)*step+off
        if b-a < step*0.5: b=a+step
        out.append([a, b-a, m])
    return out

def transcribe(path, hp=250, lo=55, hi=96, jump_pen=0.55):
    x,sr=sf.read(path,always_2d=True); y=x.mean(axis=1).astype(np.float64)
    h=hpss_harmonic(y,sr); yb=highpass(h,sr,hp)
    cands,t,sal,_=salience(yb,sr,lo=lo,hi=hi)
    pitch=viterbi(sal,cands,jump_pen=jump_pen)
    notes=segment(pitch,t)
    beat,off=tempo_grid(y,sr)
    return dict(sr=sr, dur=len(y)/sr, beat=beat, off=off,
                notes=notes, qnotes=quantise(notes,beat,off))

def dewarble(notes, max_step=2, max_run_dur=0.30, min_run=3):
    """Collapse rapid semitone/tone oscillations into one held note."""
    out=[]; i=0
    while i < len(notes):
        j=i
        while (j+1 < len(notes)
               and abs(notes[j+1][2]-notes[j][2]) <= max_step
               and notes[j+1][2] != notes[j][2]
               and notes[j][1] <= max_run_dur
               and notes[j+1][1] <= max_run_dur
               and (j==i or (notes[j+1][2]-notes[j][2])*(notes[j][2]-notes[j-1][2]) < 0)):
            j+=1
        run=notes[i:j+1]
        if len(run) >= min_run:
            tot={}
            for s,d,m in run: tot[m]=tot.get(m,0)+d
            keep=max(tot, key=lambda k:(tot[k], -abs(k-run[0][2])))
            st=run[0][0]; en=run[-1][0]+run[-1][1]
            out.append([st, en-st, keep])
        else:
            out.extend([list(n) for n in run])
        i=j+1
    return out
