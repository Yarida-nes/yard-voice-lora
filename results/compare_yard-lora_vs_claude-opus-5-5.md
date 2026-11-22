# yard-lora vs claude-opus-5-5

100 test examples, the same for both

| Measure | yard-lora | claude-opus-5-5 |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 95.0% | 97.0% |
| Decision right | 98.0% | 100.0% |
| Unsafe: acted when it should have checked | 2.0% | 0.0% |

Right only for yard-lora: 0. Right only for claude-opus-5-5: 2.
McNemar test p = 0.5000 (could be chance).
