"""Transcribe the 200 TEST clips with base Whisper small.en and with the LoRA version, the same way.

Both run through Hugging Face transformers on the GPU, so the only difference is the LoRA weights.

    laya-env/Scripts/python optional/transcribe_lora.py
-> data/audio_{clean,noisy}_wbase.jsonl and data/audio_{clean,noisy}_wlora.jsonl
"""
import json
import sys
from pathlib import Path

import jiwer
import torch
from peft import PeftModel
from transformers import WhisperForConditionalGeneration, WhisperProcessor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "optional"))
from add_noise import load  # noqa: E402
from read_unit import read_unit  # noqa: E402

BASE = "openai/whisper-small.en"


DEV = "cpu" if "--cpu" in sys.argv or not torch.cuda.is_available() else "cuda"


def transcribe(model, proc, clips, folder):
    out = []
    for c in clips:
        feats = proc.feature_extractor(load(folder / c["audio"]), sampling_rate=16000, return_tensors="pt").input_features
        with torch.no_grad(), torch.autocast(DEV, dtype=torch.float16, enabled=DEV == "cuda"):
            ids = model.generate(input_features=feats.to(DEV), max_new_tokens=80)
        out.append(proc.batch_decode(ids, skip_special_tokens=True)[0].strip())
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    data = args[0] if args else "audio"  # folder with manifest.jsonl (my_recordings works too)
    folder = ROOT / data
    clips = [json.loads(l) for l in (folder / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    proc = WhisperProcessor.from_pretrained(BASE)
    base = WhisperForConditionalGeneration.from_pretrained(BASE).to(DEV).eval()
    heard = {"wbase": transcribe(base, proc, clips, folder)}
    lora = PeftModel.from_pretrained(base, ROOT / "models" / "whisper-lora").eval()
    heard["wlora"] = transcribe(lora, proc, clips, folder)

    norm = jiwer.Compose([jiwer.ToLowerCase(), jiwer.RemovePunctuation(), jiwer.RemoveMultipleSpaces(), jiwer.Strip()])
    for tag, texts in heard.items():
        for kind in ("clean", "noisy"):
            part = [(c, t) for c, t in zip(clips, texts) if (c["noise"] == "none") == (kind == "clean")]
            if not part:
                continue
            rows = [{**c, "text": t, "original_text": c.get("original_text", c["text"])} for c, t in part]
            prefix = "audio" if data == "audio" else data.replace("/", "_")
            (ROOT / f"data/{prefix}_{kind}_{tag}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
            unit = sum(read_unit(r["text"]) == r["expected"]["unit"] for r in rows)
            wer = jiwer.wer([norm(r["original_text"]) for r in rows], [norm(r["text"]) or "-" for r in rows])
            print(f"{tag} {kind}: trailer number right {unit}/{len(rows)} | word error rate {100 * wer:.1f}%")


if __name__ == "__main__":
    main()
