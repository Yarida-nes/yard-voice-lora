# qwen3-8b vs yard-lora-s7

100 test examples, the same for both

| Measure | qwen3-8b | yard-lora-s7 |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 82.0% | 96.0% |
| Decision right | 87.0% | 98.0% |
| Unsafe: acted when it should have checked | 6.0% | 1.0% |

Right only for qwen3-8b: 0. Right only for yard-lora-s7: 14.
McNemar test p = 0.0001 (unlikely to be chance).
