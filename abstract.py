import nmt
import numpy as np
import pyworld as pw

R = 44100

def analyze(path):
    buf = nmt.sound2np(path, R=R, nchannels=1).astype(float)[:,0]
    buf /= abs(buf).max()

    _f0, t = pw.dio(buf, R)
    f0 = pw.stonemask(buf, _f0, t, R)
    sp = pw.cheaptrick(buf, f0, t, R)
    ap = pw.d4c(buf, f0, t, R)

    return buf, f0, sp, ap

def gen(f, s, a, fr_sz=5):
    synth = pw.synthesize(f, s, a, R, fr_sz).reshape((-1,1))
    synth /= abs(max(synth))    # Normalize
    return (synth * 2**15).astype(np.int16)

def blend_sp_words(sp_in, trans):
    sp = sp_in.copy()
    for wd in trans['words']:
        st_idx = int(wd['start'] * 200)
        end_idx = int(wd['end'] * 200)

        sp_sub = sp[st_idx:end_idx]
        if len(sp_sub) > 0:
            sp_sub[:] = sp_sub.mean(axis=0)
    return sp
            
def blend_sp_phones(sp, trans):
    for wd in trans['words']:
        cur_st = wd['start']
        for ph in wd['phones']:
            st_idx = int(cur_st * 200)
            end_idx = st_idx + int(ph['duration'] * 200)

            cur_st += ph['duration']

            sp_sub = sp[st_idx:end_idx]
            if len(sp_sub) > 0:
                sp_sub[:] = sp_sub.mean(axis=0)

def windowed_blend(sp, WLEN=5):
    out = sp.copy()
    for idx in range(sp.shape[1]):
        out[:,idx] = sp[:,idx:idx+WLEN].mean(axis=1)
    return out


def pitchtrack(f0, R=44100):
    dur = len(f0) / 200.0
    out = np.zeros((int(dur*R)), np.int16)

    for idx,pitch in enumerate(f0):
        o_st_idx = int((idx/200.0)*R)
        o_end_idx = int(((idx+1)/200.0)*R)

        dur = 1/200.0
        n_cycles = int(dur * pitch) # make even so that we don't click

        sinwave = 2**15 * np.sin(
            np.linspace(
                0, 2*np.pi*n_cycles,
                num=o_end_idx-o_st_idx))

        out[o_st_idx:o_end_idx] = sinwave

    return out
