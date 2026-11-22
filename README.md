# Yard voice commands: fine-tuning a small local model with LoRA

I built a practice version of a voice-command system for truck yards. A worker says something like "take 4471 to door 6", Whisper turns the speech into text, a small local model turns the text into JSON, and plain code decides whether to **ACT**, **READ_BACK** or **ASK_AGAIN**. I fine-tuned both the language model (Qwen3-8B) and Whisper with LoRA, and compared them with a cloud model (Claude) and two decision models (Laya and TypeSafe Jev).

All data here is synthetic. This is a practice version I built to learn the pipeline. It is not any company's real system or data.

## What I found

**1. LoRA fine-tuning made the local model nearly as good as a big cloud model** (100 test sentences, typed text):

| Model | Exact match | Decisions right | Unsafe ACT |
|---|---|---|---|
| Qwen3-8B, base | 82 | 87 | 6 |
| Qwen3-8B + LoRA (attention, seed 7) | 96 | 98 | 1 |
| Claude Opus 5.5 (cloud) | 97 | 100 | 0 |

The gain over the base model is not chance (McNemar p ≤ 0.001), and it held across two seeds. Training the MLP layers too (2.8× more weights) did not change the score. My model and Claude are not significantly different (p = 0.5 to 1.0), and mine runs on a laptop.

**2. The model should read and code should decide.** When the decision models Laya and Jev picked ACT / READ_BACK / ASK_AGAIN by themselves, they made 26 and 36 unsafe ACTs, because the right decision depends on yard facts that are not in the sentence. When they only read the action and the place and the rules decided, they made 3 and 0.

**3. Voice.** With computer voices (100 sentences, clean and with artificial engine noise), LoRA Whisper heard the trailer number right in 93 of 100 clips, against 80–83 for base Whisper. My two LoRA models together (Whisper to hear, Qwen to read, rules to decide) got 95 of 100 decisions right from speech.

**4. My own voice is much harder.** I recorded 22 test sentences twice, quiet and with real background noise:

| | Trailer number right, quiet / noisy (of 22) | Unsafe ACT |
|---|---|---|
| Base Whisper | 13 / 7 | 0 / 0 |
| LoRA Whisper | 15 / 12 | 0 / 0 |

Whisper heard "eight" as "egg", "door" as "draw" and "dock" as "dog". LoRA Whisper was trained only on computer voices, so it did not learn my accent. But the rules still stopped every wrong command, so the system got slower, not more dangerous.

## Audio data

- `my_recordings/`: my own voice, used only for testing. `full100/` has all 100 test sentences (quiet); the `test-XXXX_noisy.wav` files are 22 of them recorded again with real background noise.
- `audio_train/`: synthetic (AI) voices for the 210 training sentences, clean and with engine noise, used to train Whisper with LoRA. Six voices that are not used in the test.
- `audio/`: synthetic voices for the 100 test sentences, clean and with engine noise, in four other voices.

## Limits

- Synthetic data: 90 of the 100 test sentences come from the same templates as the training data. On the 10 hand-written ones, fine-tuning did not beat the base model (7–8 vs 8).
- The voice tests use computer voices and artificial noise, plus 22 recordings of one real person (me).
- The trailer-number reader used with Laya and Jev, and the Laya routing threshold, were set after seeing the test sentences.

## What I'd do next

- Write 20–30 more hand-written test sentences, and add training examples for cancellations and doors that don't exist.
- Train Whisper on real voices with different accents.
- Try a smaller model (Qwen3-1.7B) fine-tuned the same way.

## How to run it

- `notebooks/train_lora_colab.ipynb`: LoRA fine-tune of Qwen3-8B on a free Colab T4, export to GGUF for Ollama.
- `optional/run_model.py`, `optional/score.py`, `optional/compare.py`: test a model in Ollama, score it, McNemar test.
- `optional/run_claude.py`, `optional/run_laya_fields.py`, `optional/run_jev.py`: the cloud and decision-model tests.
- `optional/make_audio.py`, `optional/add_noise.py`, `optional/transcribe.py`: the voice test. `optional/make_train_audio.py`, `optional/train_whisper_lora.py`, `optional/transcribe_lora.py`: Whisper LoRA.
- `results/`: every prediction, score and comparison; `results/model_comparison_all.xlsx` has them all in one workbook.

I used Claude Code as a coding assistant and tutor during this project.

---

# The practice kit

The rest of this page is the original kit I started from.

## What's ready

| File | What it is |
|---|---|
| `data/yard.json` | The pretend yard: 20 trailers (4 pairs of look-alike numbers such as 4471 / 4417), 8 doors (2 and 5 are busy), staging and parking |
| `LABELLING-RULES.md` | How each sentence is labelled, and the 8 decision rules |
| `data/train.jsonl` | 210 training examples |
| `data/test.jsonl` | 100 test examples: 90 generated plus 10 hand-written tricky ones. **Never train on these.** |
| `data/train_conversations.jsonl` | The training examples in the format the Colab notebook expects |
| `data/handwritten_tricky.csv` | The hand-written test sentences. Add your own here (aim for 30). |
| `notebooks/train_lora_colab.ipynb` | Colab notebook: LoRA fine-tune of Qwen3-1.7B, export for Ollama |
| `src/generate_data.py` | Makes all the data files again from templates |
| `src/rules.py` | The decision rules as code |
| `src/prompt.py` | The prompt used for training. **Use exactly this prompt when testing.** |
| `src/schema.py` | The JSON shape, as a Pydantic model (give it to Ollama's `format` option) |
| `optional/` | Scripts for scoring and for audio tests, if you want them later |

One test example:

```json
{"text": "bring 3851 up to door 4 mate",
 "expected": {"action": "move", "unit": "3851", "to": "door_04"},
 "decision": "READ_BACK", "kind": "move_lookalike"}
```

The test set has ACT 45, READ_BACK 25 and ASK_AGAIN 30. `kind` says what each example tests (look-alike numbers, busy doors, corrections, missing door, unknown trailer, unclear speech, and so on), so you can see which kinds the model gets wrong.

## Steps

1. **Read `LABELLING-RULES.md`** and look at 10 examples in `data/test.jsonl`. Change any rule you disagree with.
2. **Add your own tricky sentences** to `data/handwritten_tricky.csv`, then rebuild the data:
   ```
   pip install pydantic
   python src/generate_data.py
   ```
   `--n 400` makes more examples. `--seed 1` makes a different set.
3. **Test the base model** (`qwen3:1.7b` in Ollama) on `data/test.jsonl`, with the prompt from `src/prompt.py`, the schema from `src/schema.py` as `format`, and temperature 0. Work out the decision for each answer with `rules.decide()`. Save the results: this is the "before" score.
4. **Train in Colab**: open `notebooks/train_lora_colab.ipynb` in Google Colab, set the runtime to T4 GPU, run every cell, and upload `data/train_conversations.jsonl` when it asks.
5. **Load the trained model into Ollama** (the notebook's last cell explains how) and run the same test again: the "after" score.
6. **Write up**: before and after, which kinds improved, 3 mistakes it still makes, and what you'd try next.

## Things to know

- The training sentences and the test sentences come from the same templates, so the generated test examples are easier than real speech. The hand-written examples are the fairer test. Report them separately.
- The most important number is how often it **acted when it should have checked** (said ACT when the right answer was READ_BACK or ASK_AGAIN). That's the mistake that moves the wrong trailer.
- The training notebook is adapted from the LocoLabo capstone notebook by Michael Borck (Curtin).
