# yard-lora-mlp vs yard-lora-mlp-s7

100 test examples, the same for both

| Measure | yard-lora-mlp | yard-lora-mlp-s7 |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 95.0% | 96.0% |
| Decision right | 98.0% | 98.0% |
| Unsafe: acted when it should have checked | 1.0% | 1.0% |

Right only for yard-lora-mlp: 0. Right only for yard-lora-mlp-s7: 1.
McNemar test p = 1.0000 (could be chance).
