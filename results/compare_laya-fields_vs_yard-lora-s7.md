# laya-fields vs yard-lora-s7

100 test examples, the same for both

| Measure | laya-fields | yard-lora-s7 |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 74.0% | 96.0% |
| Decision right | 93.0% | 98.0% |
| Unsafe: acted when it should have checked | 3.0% | 1.0% |

Right only for laya-fields: 2. Right only for yard-lora-s7: 24.
McNemar test p = 0.0000 (unlikely to be chance).
