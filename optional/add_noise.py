"""Make noisy copies of the speech clips without ffmpeg, using artificial engine-like noise.

There is no real yard recording here, so the noise is made in code: low rumble (brown noise) plus
an idling-engine hum (30 Hz and its harmonics, pulsing slightly). It is a stand-in, not real yard noise.

python optional/add_noise.py --snr 5     (after make_audio.py; adds the noisy clips to audio/manifest.jsonl)
SNR = signal-to-noise ratio in decibels: 5 dB means the speech is only a little louder than the noise.
"""
import argparse
import json
import wave
from pathlib import Path

import av
import numpy as np

ROOT = Path(__file__).parent.parent
AUDIO = ROOT / "audio"
RATE = 16000


def load(path):
    """Decode an audio file to 16 kHz mono float samples."""
    with av.open(str(path)) as f:
        rs = av.AudioResampler(format="flt", layout="mono", rate=RATE)
        parts = [r.to_ndarray().ravel() for frame in f.decode(audio=0) for r in rs.resample(frame)]
        parts += [r.to_ndarray().ravel() for r in rs.resample(None)]
    return np.concatenate(parts).astype(np.float32)


def engine_noise(n, rng):
    brown = np.cumsum(rng.normal(size=n))
    brown -= np.convolve(brown, np.ones(2000) / 2000, mode="same")  # keep the rumble, drop the drift
    brown /= np.abs(brown).max() + 1e-9
    t = np.arange(n) / RATE
    pulse = 1 + 0.3 * np.sin(2 * np.pi * 2.5 * t)  # engine idling unevenly
    hum = sum(np.sin(2 * np.pi * 30 * k * t + rng.uniform(0, 6.3)) / k for k in range(1, 8)) * pulse
    hum /= np.abs(hum).max() + 1e-9
    return 0.6 * brown + 0.4 * hum + 0.05 * rng.normal(size=n)


def save(path, x):
    x = np.clip(x / (np.abs(x).max() + 1e-9) * 0.9, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snr", type=float, default=5.0)
    args = ap.parse_args()
    rng = np.random.default_rng(7)
    rows = [json.loads(l) for l in (AUDIO / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    clean = [r for r in rows if r["noise"] == "none"]
    out = list(clean)
    for r in clean:
        speech = load(AUDIO / r["audio"])
        noise = engine_noise(len(speech), rng)
        p_s, p_n = np.mean(speech ** 2), np.mean(noise ** 2)
        noise *= np.sqrt(p_s / (p_n * 10 ** (args.snr / 10)))
        name = r["audio"].replace("_clean.mp3", "_noisy.wav")
        save(AUDIO / name, speech + noise)
        out.append({**r, "audio": name, "noise": f"engine {args.snr:g} dB"})
    (AUDIO / "manifest.jsonl").write_text("".join(json.dumps(m) + "\n" for m in out), encoding="utf-8")
    print(f"Saved {len(clean)} noisy clips; manifest now has {len(out)} clips")


if __name__ == "__main__":
    main()
