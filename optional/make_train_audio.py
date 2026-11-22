"""Speech for the 210 TRAINING sentences, to fine-tune Whisper with LoRA.

Uses different voices from the test clips (make_audio.py), so the test checks whether Whisper learned
the yard words, not the test voices. Each sentence gets a clean copy and an engine-noise copy.

python optional/make_train_audio.py      -> audio_train/ + audio_train/manifest.jsonl
"""
import asyncio
import json
import sys
from pathlib import Path

import edge_tts
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "optional"))
from add_noise import engine_noise, load, save  # noqa: E402

OUT = ROOT / "audio_train"
VOICES = ["en-US-GuyNeural", "en-US-JennyNeural", "en-NZ-MitchellNeural", "en-CA-ClaraNeural",
          "en-ZA-LukeNeural", "en-GB-SoniaNeural"]


async def speak(text, voice, path):
    for attempt in range(10):
        try:
            await edge_tts.Communicate(text, voice).save(str(path))
            return
        except edge_tts.exceptions.NoAudioReceived:
            if attempt == 9:
                raise
            await asyncio.sleep(3 * (attempt + 1))


def main():
    rows = [json.loads(l) for l in (ROOT / "data/train.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(42)
    manifest = []
    for i, r in enumerate(rows):
        voice = VOICES[i % len(VOICES)]
        clean = OUT / f"{r['id']}_clean.mp3"
        if not clean.exists():
            asyncio.run(speak(r["text"], voice, clean))
        manifest.append({"id": r["id"], "text": r["text"], "audio": clean.name, "voice": voice, "noise": "none"})
        noisy = OUT / f"{r['id']}_noisy.wav"
        speech = load(clean)
        noise = engine_noise(len(speech), rng)
        snr = rng.uniform(3, 15)  # vary the noise level in training
        noise *= np.sqrt(np.mean(speech ** 2) / (np.mean(noise ** 2) * 10 ** (snr / 10)))
        save(noisy, speech + noise)
        manifest.append({"id": r["id"], "text": r["text"], "audio": noisy.name, "voice": voice, "noise": f"engine {snr:.0f} dB"})
        if (i + 1) % 30 == 0:
            print(f"{i + 1}/{len(rows)}")
    (OUT / "manifest.jsonl").write_text("".join(json.dumps(m) + "\n" for m in manifest), encoding="utf-8")
    print(f"Saved {len(manifest)} training clips")


if __name__ == "__main__":
    main()
