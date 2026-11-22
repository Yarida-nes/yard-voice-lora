"""Run Whisper on my own recordings in my_recordings/ and save what it heard.

Name each file by its test id: test-0090.m4a (quiet) and test-0090_noisy.m4a (with real noise).
Any of .m4a .mp3 .wav works.

python optional/transcribe_my_voice.py           -> data/myvoice_clean.jsonl, data/myvoice_noisy.jsonl
python optional/transcribe_my_voice.py --hint    -> the same with the yard hint (…_hint.jsonl)
Then run the models on them, e.g.:
    python optional/run_jev.py --data myvoice_clean.jsonl --name jev-myvoice-clean
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "optional"))
from add_noise import load as load_audio  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402
from read_unit import read_unit  # noqa: E402
from rules import YARD  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--hint", action="store_true")
    args = ap.parse_args()

    test = {r["id"]: r for r in map(json.loads, (ROOT / "data/test.jsonl").read_text(encoding="utf-8").splitlines()) if r}
    files = sorted(p for p in (ROOT / "my_recordings").iterdir() if p.suffix.lower() in (".m4a", ".mp3", ".wav"))
    unknown = [p.name for p in files if p.stem.removesuffix("_noisy") not in test]
    if unknown:
        print("Skipping files not named by a test id:", ", ".join(unknown))

    whisper = WhisperModel(args.model, device="cpu", compute_type="int8")
    hint = ("Yard radio. Trailers " + ", ".join(YARD["trailers"]) + ". Doors one to eight, staging, parking.") if args.hint else None
    out = {"clean": [], "noisy": []}
    for p in files:
        tid = p.stem.removesuffix("_noisy")
        if tid not in test:
            continue
        kind = "noisy" if p.stem.endswith("_noisy") else "clean"
        segments, _ = whisper.transcribe(load_audio(p), language="en", initial_prompt=hint)
        heard = " ".join(s.text.strip() for s in segments).strip()
        r = test[tid]
        out[kind].append({**r, "text": heard, "original_text": r["text"], "audio": p.name, "noise": kind})
        print(f"{kind:>5}  said:  {r['text']}\n{'':>5}  heard: {heard}")

    suffix = "_hint" if args.hint else ""
    for kind, rows in out.items():
        if rows:
            (ROOT / f"data/myvoice_{kind}{suffix}.jsonl").write_text("".join(json.dumps(o) + "\n" for o in rows), encoding="utf-8")
            right = sum(read_unit(o["text"]) == o["expected"]["unit"] for o in rows)
            print(f"{kind}: {len(rows)} recordings, trailer number heard right {right}/{len(rows)}")


if __name__ == "__main__":
    main()
