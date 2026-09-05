import numpy as np
from scipy import signal
SR=44100

def make_ir(rt60=0.4, predelay=0.012, damp_hz=5000.0, seed=7, sr=SR):
    """Exponentially-decaying, lowpassed noise burst — a simple synthetic room."""
    n=int(rt60*1.6*sr)
    rng=np.random.default_rng(seed)
    t=np.arange(n)/sr
    ir=rng.standard_normal(n)*np.exp(-t*6.9077/rt60)
    b,a=signal.butter(2, min(damp_hz,sr/2*0.95)/(sr/2), btype='low')
    ir=signal.lfilter(b,a,ir)
    ir[:int(0.002*sr)]*=np.linspace(0,1,int(0.002*sr))   # soften the very front
    ir/=np.sqrt((ir**2).sum())+1e-12
    return np.concatenate([np.zeros(int(predelay*sr)), ir])

def reverb(x, rt60=0.4, wet=0.22, predelay=0.012, damp_hz=5000.0, sr=SR):
    ir=make_ir(rt60, predelay, damp_hz, sr=sr)
    w=signal.fftconvolve(x, ir)[:len(x)+len(ir)]
    d=np.zeros(len(w)); d[:len(x)]=x
    w*= (np.abs(x).max()+1e-12)/(np.abs(w).max()+1e-12)   # match levels before mixing
    return (1-wet)*d + wet*w
