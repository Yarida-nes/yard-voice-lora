# claude-opus-5-5 vs yard-lora-mlp-s7

100 test examples, the same for both

| Measure | claude-opus-5-5 | yard-lora-mlp-s7 |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 97.0% | 96.0% |
| Decision right | 100.0% | 98.0% |
| Unsafe: acted when it should have checked | 0.0% | 1.0% |

Right only for claude-opus-5-5: 1. Right only for yard-lora-mlp-s7: 0.
McNemar test p = 1.0000 (could be chance).
