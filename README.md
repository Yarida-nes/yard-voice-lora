# Yard voice commands: practice data and training kit

A practice version of a yard voice-command system: a worker says something like "take 4471 to door 6", a small local model turns it into JSON, and code decides whether to **ACT**, **READ_BACK** or **ASK_AGAIN**. All data here is synthetic (made up). It is not any company's real system or data.

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
