# yard-lora vs yard-lora-mlp

100 test examples, the same for both

| Measure | yard-lora | yard-lora-mlp |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 95.0% | 95.0% |
| Decision right | 98.0% | 98.0% |
| Unsafe: acted when it should have checked | 2.0% | 1.0% |

Right only for yard-lora: 1. Right only for yard-lora-mlp: 1.
McNemar test p = 1.0000 (could be chance).
