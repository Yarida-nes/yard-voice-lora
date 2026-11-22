"""Turn test sentences into speech, with and without background noise.

python optional/make_audio.py --count 30
Put a noise recording (wav or mp3, e.g. a truck idling) at audio/noise.wav first.
Needs ffmpeg for the noisy copies. List voices with: edge-tts --list-voices
"""
import argparse
import asyncio
import json
import random
import shutil
import subprocess
from pathlib import Path

import edge_tts

ROOT = Path(__file__).parent.parent
AUDIO = ROOT / "audio"
VOICES = ["en-AU-NatashaNeural", "en-AU-WilliamNeural", "en-GB-RyanNeural", "en-IN-NeerjaNeural"]


async def speak(text: str, voice: str, path: Path) -> None:
    for attempt in range(5):  # the online voice service sometimes drops a request
        try:
            await edge_tts.Communicate(text, voice).save(str(path))
            return
        except edge_tts.exceptions.NoAudioReceived:
            if attempt == 4:
                raise
            await asyncio.sleep(2 * (attempt + 1))


def add_noise(clean: Path, noise: Path, out: Path, volume: float) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clean), "-stream_loop", "-1", "-i", str(noise),
                    "-filter_complex", f"[1]volume={volume}[n];[0][n]amix=inputs=2:duration=first:normalize=0",
                    "-ar", "16000", "-ac", "1", str(out)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=30)
    ap.add_argument("--noise-volume", type=float, default=0.5)
    args = ap.parse_args()

    rows = [json.loads(l) for l in (ROOT / "data/test.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = random.Random(7).sample(rows, min(args.count, len(rows)))
    AUDIO.mkdir(exist_ok=True)
    noise = next((p for p in (AUDIO / "noise.wav", AUDIO / "noise.mp3") if p.exists()), None)
    if noise and not shutil.which("ffmpeg"):
        print("ffmpeg not found, so only clean audio will be made")
        noise = None

    manifest = []
    for i, r in enumerate(rows):
        voice = VOICES[i % len(VOICES)]
        clean = AUDIO / f"{r['id']}_clean.mp3"
        asyncio.run(speak(r["text"], voice, clean))
        manifest.append({**r, "audio": clean.name, "voice": voice, "noise": "none"})
        if noise:
            noisy = AUDIO / f"{r['id']}_noisy.wav"
            add_noise(clean, noise, noisy, args.noise_volume)
            manifest.append({**r, "audio": noisy.name, "voice": voice, "noise": noise.name})
        print(f"{i + 1}/{len(rows)}  {voice}  {r['text']}")

    (AUDIO / "manifest.jsonl").write_text("".join(json.dumps(m) + "\n" for m in manifest), encoding="utf-8")
    print(f"Saved {len(manifest)} clips and audio/manifest.jsonl")


if __name__ == "__main__":
    main()
