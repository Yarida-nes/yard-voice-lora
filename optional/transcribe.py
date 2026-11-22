"""Speech to text on the clips, then measure how much Whisper got wrong.

python optional/transcribe.py             -> data/audio_test.jsonl and results/whisper.md
python optional/transcribe.py --hint      -> gives Whisper the yard's trailer numbers and door names first
Then: python optional/run_model.py --model <model> --data data/audio_test.jsonl --name <model>-audio
"""
import argparse
import json
from pathlib import Path

import jiwer
from faster_whisper import WhisperModel

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rules import YARD
from add_noise import load as load_audio  # decodes to 16 kHz samples (faster-whisper's own loader fails with av 19)

ROOT = Path(__file__).parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--hint", action="store_true")
    args = ap.parse_args()

    clips = [json.loads(l) for l in (ROOT / "audio/manifest.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    whisper = WhisperModel(args.model, device="cpu", compute_type="int8")
    hint = ("Yard radio. Trailers " + ", ".join(YARD["trailers"]) + ". Doors one to eight, staging, parking.") if args.hint else None

    out = []
    for c in clips:
        segments, _ = whisper.transcribe(load_audio(ROOT / "audio" / c["audio"]), language="en", initial_prompt=hint)
        heard = " ".join(s.text.strip() for s in segments).strip()
        out.append({**c, "text": heard, "original_text": c["text"]})
        print(f"{c['noise']:>10}  said: {c['text']}\n{'':>10}  heard: {heard}")

    suffix = "-hint" if args.hint else ""
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / f"data/audio_test{suffix}.jsonl").write_text("".join(json.dumps(o) + "\n" for o in out), encoding="utf-8")

    norm = jiwer.Compose([jiwer.ToLowerCase(), jiwer.RemovePunctuation(), jiwer.RemoveMultipleSpaces(), jiwer.Strip()])
    md = [f"# Whisper {args.model}{' with hint' if args.hint else ''}", "",
          "| Noise | Clips | Word error rate |", "|---|---|---|"]
    for noise in sorted({o["noise"] for o in out}):
        part = [o for o in out if o["noise"] == noise]
        wer = jiwer.wer([norm(o["original_text"]) for o in part], [norm(o["text"]) or "-" for o in part])
        md.append(f"| {noise} | {len(part)} | {100 * wer:.1f}% |")
    md += ["", "Word error rate counts \"forty-four\" vs \"44\" as an error, so also read the transcripts.",
           "The fairer test is the next step: run the model on what Whisper heard and score it.",
           "", "| Said | Heard | Noise |", "|---|---|---|"]
    md += [f"| {o['original_text']} | {o['text']} | {o['noise']} |" for o in out]
    (ROOT / f"results/whisper{suffix}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Saved data/audio_test{suffix}.jsonl and results/whisper{suffix}.md")


if __name__ == "__main__":
    main()
