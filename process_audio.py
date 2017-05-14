import abstract

import json
import nmt
import numpy as np
from scipy.ndimage.filters import gaussian_filter
import os
import subprocess
import sys

def process(audio_path, outdir, do_transcribe=True):
    try:
        os.makedirs(outdir)
    except OSError:
        pass

    # Start transcription
    if do_transcribe:
        p = subprocess.Popen([
            'curl',
            '-o', os.path.join(outdir, 'align.json'),
            '-X', 'POST',
            '-F', 'audio=@%s' % (audio_path),
            'http://localhost:8765/transcriptions?async=false'])

    # Generate various effects

    buf, f0, sp, ap = abstract.analyze(audio_path)

    half_pitch = f0.copy() / 2
    double_pitch = f0.copy() * 2

    blur_sp = abstract.windowed_blend(sp, WLEN=50)


    # Output a bunch of audio

    path = os.path.join(outdir, 'raw.mp3')
    if not os.path.exists(path):
        nmt.np2sound(
            (buf*2**15).astype(np.int16),
            path)
    path = os.path.join(outdir, 'flat.mp3')
    if not os.path.exists(path):
        flat_pitch = f0.copy()
        flat_pitch[flat_pitch>0] = f0[f0>0].mean()
        nmt.np2sound(
            abstract.gen(flat_pitch, sp, ap),
            path)
    path = os.path.join(outdir, 'half.mp3')
    if not os.path.exists(path):
        nmt.np2sound(
            abstract.gen(half_pitch, sp, ap),
            path)
    path = os.path.join(outdir, 'double.mp3')
    if not os.path.exists(path):
        nmt.np2sound(
            abstract.gen(double_pitch, sp, ap),
            path)
    path = os.path.join(outdir, 'blur3.mp3')
    if not os.path.exists(path):
        npblur3 = gaussian_filter(sp, sigma=3)
        nmt.np2sound(
            abstract.gen(f0, npblur3, ap),
            path)
    path = os.path.join(outdir, 'blur30.mp3')
    if not os.path.exists(path):
        npblur30 = gaussian_filter(sp, sigma=30)
        nmt.np2sound(
            abstract.gen(f0, npblur30, ap),
            path)
    path = os.path.join(outdir, 'fast.mp3')    
    if not os.path.exists(path):
        nmt.np2sound(
            abstract.gen(f0, sp, ap, 3),
            path)
    path = os.path.join(outdir, 'slow.mp3')
    if not os.path.exists(path):
        nmt.np2sound(
            abstract.gen(f0, sp, ap, 10),
            path)

    # Wait for transcription to finish
    if do_transcribe:
        p.wait()

        trans = json.load(open(os.path.join(outdir, 'align.json')))

        path = os.path.join(outdir, 'blend.mp3')
        if not os.path.exists(path):
            wd_blend = abstract.blend_sp_words(sp, trans)

            nmt.np2sound(
                abstract.gen(f0, wd_blend, ap),
                path)

if __name__=='__main__':
    audio_path = sys.argv[1]
    outdir = sys.argv[2]

    process(audio_path, outdir)
