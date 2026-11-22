# jev vs yard-lora-s7

100 test examples, the same for both

| Measure | jev | yard-lora-s7 |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 97.0% | 96.0% |
| Decision right | 100.0% | 98.0% |
| Unsafe: acted when it should have checked | 0.0% | 1.0% |

Right only for jev: 1. Right only for yard-lora-s7: 0.
McNemar test p = 1.0000 (could be chance).
