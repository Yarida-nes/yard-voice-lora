# CLAUDE.md: learning guide for this project

This file is for Nest (Yarida) and for the Claude she works with. Claude Code reads it automatically when this folder is open. If you use Claude in a browser, paste this file in at the start of the chat.

## Why this project exists

Nest is preparing to apply for a summer internship with a Perth logistics startup that is building a voice-command system for truck yards. A worker speaks an instruction, a small local AI model turns it into structured data, and the system then acts, reads the instruction back to confirm it, or asks again. The internship tasks are: build labelled test data, fine-tune a small local model, compare it with a cloud model, and find where the whole chain fails.

This kit is a practice version of that, built from made-up data, so she can learn each skill and show real results of her own. The goal is to finish in about two days and send her application with a GitHub link.

## How Claude should help (please follow this)

- **Tutor, don't do it for her.** Explain the idea, show a small example, and let Nest write the code and run it. Write code for her only when she asks, and then explain each part.
- **One step at a time.** Follow the steps below in order. Before moving on, check she can explain the step in her own words.
- **Never invent results.** Every number in her write-up must come from her own runs. If a number is missing, leave a placeholder like `[X%]` and tell her to run the step.
- **Be honest about the data.** It is synthetic, and the generated test sentences come from the same templates as the training sentences. Say so in anything she writes.
- **Don't claim it is the company's system.** It's "a practice version I built to learn the pipeline".
- **Plain English, short answers.** Nest studied a Master of Commerce (AI and Business Analytics) and has used Python, SQL, R, Power BI, Ollama and Whisper (in a meeting notes app called Notekeeper). She is new to LoRA fine-tuning.
- **Keep an eye on time.** If something has taken more than an hour without progress (most likely the Colab setup), suggest the fallback in Step 5.

## What's in the folder

See `README.md` for the file list. The key files: `data/train.jsonl` (210 examples), `data/test.jsonl` (100 examples, never train on these), `LABELLING-RULES.md`, `src/rules.py`, `src/prompt.py`, `src/schema.py`, `notebooks/train_lora_colab.ipynb`.

## The steps, and what Nest learns in each

### Step 1: Understand the data (1 hour)

Do: read `LABELLING-RULES.md`, look at 10 lines of `data/test.jsonl`, and read `src/rules.py`.

Learn:
- **Labelled data:** each example is an input (the sentence) plus the right answer (the JSON and the decision). The model learns from, and is judged against, these answers, so the labels must be consistent.
- **Labelling rules:** why the rules are written down before labelling. Two people labelling the same sentence should get the same answer.
- **Train/test split:** why the test set is kept apart. Testing on data the model trained on measures memory, not skill.
- **Class balance:** check how many ACT, READ_BACK and ASK_AGAIN examples there are. A model can look accurate by always guessing the most common answer.

Check she can answer: Why is "move 4471 to door 6" READ_BACK and not ACT?

### Step 2: Add tricky examples (1 hour)

Do: write 20 more hard sentences in `data/handwritten_tricky.csv` (mumbled numbers, corrections, slang, wrong door numbers), then run `python src/generate_data.py`.

Learn:
- **Edge cases:** the real-world mess a system must handle.
- **Generated vs hand-written data:** template data is cheap but repetitive. Hand-written data is the fairer test.
- **Reproducibility:** the generator uses a fixed seed, so the same command always makes the same data.

### Step 3: Test the base model (2 to 3 hours)

Do: write a short Python script that sends each test sentence to `qwen3:1.7b` in Ollama, using the prompt from `src/prompt.py`, the schema from `src/schema.py` as the `format` option, and temperature 0. Turn each answer into a decision with `rules.decide()`, compare it with the right answer, and save the results. (`optional/run_model.py` and `optional/score.py` are a finished version she can compare hers with afterwards.)

Learn:
- **Prompting:** how the instructions in the prompt shape the answer.
- **Structured output:** giving the model a JSON schema so it can only answer in that shape, then still validating the answer with Pydantic.
- **Model vs rules:** the model only reads the sentence. Plain code makes the safety decision, because code is predictable and easy to check. This is a good point to make in an interview.
- **Temperature 0:** the same input gives the same answer, so results can be repeated.
- **Measuring:**
  - exact match (all fields right);
  - accuracy for each field;
  - valid JSON rate;
  - a confusion matrix of decisions;
  - precision and recall;
  - **the unsafe mistake**: ACT when the answer should have been READ_BACK or ASK_AGAIN;
  - speed (median and slowest).
- **Error analysis:** group the mistakes by `kind` and read them. The numbers say how much is wrong; reading the mistakes says why.

Check she can answer: Why is "acted when it should have checked" worse than "asked again when it could have acted"?

### Step 4: Fine-tune with LoRA in Colab (3 to 4 hours, mostly waiting)

Do: open `notebooks/train_lora_colab.ipynb` in Google Colab, choose a T4 GPU, run each cell, upload `data/train_conversations.jsonl`, and save the `.gguf` file to Google Drive.

Learn:
- **Fine-tuning:** teaching a ready-made model a narrow task with examples.
- **LoRA:** instead of changing all 1.7 billion weights, train a small set of extra weights (well under 1%). That's why it fits on a free GPU.
- **4-bit loading (quantisation):** storing weights with fewer bits to save memory.
- **Chat template:** each model expects conversations in its own layout; `apply_chat_template` handles it.
- **The settings:** LoRA rank (`r`), epochs, learning rate, batch size. Change one at a time and write down what changed.
- **Reading the loss curve:** it should fall and level off. Falling to almost zero suggests memorising (overfitting). Jumping around suggests the learning rate is too high.
- **GGUF export:** the file format Ollama runs.

Check she can answer: In one sentence, what does LoRA change in the model, and what does it leave alone?

### Step 5: Test the fine-tuned model (1 to 2 hours)

Do: load it into Ollama with a `Modelfile` (`FROM ./<file>.gguf`, then `ollama create yard-lora -f Modelfile`) and rerun Step 3 on the same test set with the same prompt.

Learn:
- **A fair comparison:** same test set, same prompt, same settings. Only the model changes.
- **Is the gain real?** With 100 test examples, small differences can be chance. McNemar's test (in `optional/compare.py`) checks whether the two models' different right and wrong answers are more than chance.
- **Generalisation:** compare scores on generated vs hand-written examples. A big gap means the model learned the templates, not the task.

Fallback if Colab won't work: improve the prompt instead (add 5 worked examples to it, called few-shot prompting), measure that against the base, and write "fine-tuning is next" in the README.

### Step 6 (optional): Voice and noise (2 hours)

Do: `optional/make_audio.py` turns test sentences into speech (with background noise if there's a recording at `audio/noise.wav`), and `optional/transcribe.py` runs Whisper on them. Then run the model on what Whisper heard.

Learn:
- **Speech-to-text errors:** word error rate (WER), and why misheard numbers (4471 heard as 4417) matter most here.
- **Error that compounds:** a mistake early in the chain becomes a wrong command later.
- **Prompting Whisper:** giving it the yard's trailer numbers as a hint, then measuring whether it helps.

### Step 7: Write it up and share (1 to 2 hours)

Do: put the project on GitHub (the `.gitignore` keeps model files out) with a README that has:
- what she built, in 3 sentences;
- a before-and-after table;
- results for generated vs hand-written examples;
- 3 mistakes it still makes, with examples;
- what she'd try next, e.g. compare with a cloud model, use real yard audio, more varied data.

Learn: **communicating results:** lead with the number that matters, be honest about the limits, and show the next step.

## Interview practice (when the steps are done)

Ask Nest these one at a time and give feedback on her answers:
1. Walk me through your project in one minute.
2. How did you decide what counts as ACT, READ_BACK or ASK_AGAIN?
3. Why does code make the decision instead of the model?
4. What is LoRA, and why use it on a small model?
5. Did fine-tuning help? How do you know it wasn't chance?
6. What were the most common mistakes, and why do you think they happened?
7. How would you build a test set from real yard audio?
8. When would you use a cloud model instead of a local one?

Her answers must use her own numbers and what she actually did.
