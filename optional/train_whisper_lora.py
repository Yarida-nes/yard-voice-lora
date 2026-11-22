"""Fine-tune Whisper small.en with LoRA on speech of the 210 TRAINING sentences, on the laptop GPU.

Same idea as the Qwen LoRA: Whisper's own weights stay frozen and small extra weights are trained
in its attention layers (q_proj and v_proj), so it learns yard words and how numbers are said here.

Run with the GPU environment, from the project folder:
    laya-env/Scripts/python optional/train_whisper_lora.py
Saves the LoRA weights to models/whisper-lora (models/ is not committed).
"""
import json
import random
import sys
import time
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from transformers import WhisperForConditionalGeneration, WhisperProcessor

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "optional"))
from add_noise import load  # noqa: E402

BASE = "openai/whisper-small.en"
EPOCHS, BATCH, LR, SEED = 4, 8, 5e-4, 42


def main():
    random.seed(SEED)
    torch.manual_seed(SEED)
    dev = "cuda"
    proc = WhisperProcessor.from_pretrained(BASE)
    model = WhisperForConditionalGeneration.from_pretrained(BASE).to(dev)
    model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                                             target_modules=["q_proj", "v_proj"]))
    model.print_trainable_parameters()

    rows = [json.loads(l) for l in (ROOT / "audio_train/manifest.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    print("loading", len(rows), "training clips")
    data = []
    for r in rows:
        feats = proc.feature_extractor(load(ROOT / "audio_train" / r["audio"]), sampling_rate=16000,
                                       return_tensors="pt").input_features[0]
        labels = proc.tokenizer(r["text"]).input_ids
        data.append((feats, labels))

    start_id = model.config.decoder_start_token_id
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=LR)
    steps = EPOCHS * ((len(data) + BATCH - 1) // BATCH)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 20) * max(0.0, 1 - s / steps))
    scaler = torch.amp.GradScaler("cuda")
    model.train()
    t0, step = time.time(), 0
    for epoch in range(EPOCHS):
        random.shuffle(data)
        total = 0.0
        for i in range(0, len(data), BATCH):
            batch = data[i:i + BATCH]
            feats = torch.stack([b[0] for b in batch]).to(dev)
            n = max(len(b[1]) for b in batch)
            labels = torch.full((len(batch), n), -100, dtype=torch.long)
            for j, (_, lab) in enumerate(batch):
                labels[j, :len(lab)] = torch.tensor(lab)
            if (labels[:, 0] == start_id).all():  # the model adds the start token itself
                labels = labels[:, 1:]
            with torch.autocast("cuda", dtype=torch.float16):
                loss = model(input_features=feats, labels=labels.to(dev)).loss
            opt.zero_grad()
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            step += 1
            total += loss.item() * len(batch)
            if step % 10 == 0:
                print(f"step {step}/{steps}  loss {loss.item():.3f}")
        print(f"epoch {epoch + 1}: mean loss {total / len(data):.3f}")
    out = ROOT / "models" / "whisper-lora"
    model.save_pretrained(out)
    print(f"trained in {time.time() - t0:.0f} s, saved {out}")


if __name__ == "__main__":
    main()
