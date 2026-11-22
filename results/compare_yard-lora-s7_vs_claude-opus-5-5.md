# yard-lora-s7 vs claude-opus-5-5

100 test examples, the same for both

| Measure | yard-lora-s7 | claude-opus-5-5 |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 96.0% | 97.0% |
| Decision right | 98.0% | 100.0% |
| Unsafe: acted when it should have checked | 1.0% | 0.0% |

Right only for yard-lora-s7: 0. Right only for claude-opus-5-5: 1.
McNemar test p = 1.0000 (could be chance).
