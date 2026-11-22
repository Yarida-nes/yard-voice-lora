# qwen3-8b vs yard-lora-mlp

100 test examples, the same for both

| Measure | qwen3-8b | yard-lora-mlp |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 82.0% | 95.0% |
| Decision right | 87.0% | 98.0% |
| Unsafe: acted when it should have checked | 6.0% | 1.0% |

Right only for qwen3-8b: 1. Right only for yard-lora-mlp: 14.
McNemar test p = 0.0010 (unlikely to be chance).
