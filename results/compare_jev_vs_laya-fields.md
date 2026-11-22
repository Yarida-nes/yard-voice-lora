# jev vs laya-fields

100 test examples, the same for both

| Measure | jev | laya-fields |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 97.0% | 74.0% |
| Decision right | 100.0% | 93.0% |
| Unsafe: acted when it should have checked | 0.0% | 3.0% |

Right only for jev: 25. Right only for laya-fields: 2.
McNemar test p = 0.0000 (unlikely to be chance).
