# qwen3-8b vs claude-opus-5-5

100 test examples, the same for both

| Measure | qwen3-8b | claude-opus-5-5 |
|---|---|---|
| Valid JSON | 100.0% | 100.0% |
| Exact match | 82.0% | 97.0% |
| Decision right | 87.0% | 100.0% |
| Unsafe: acted when it should have checked | 6.0% | 0.0% |

Right only for qwen3-8b: 0. Right only for claude-opus-5-5: 15.
McNemar test p = 0.0001 (unlikely to be chance).
