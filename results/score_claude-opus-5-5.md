# claude-opus-5-5

100 test examples

| Measure | Result |
|---|---|
| Valid JSON | 100.0% |
| Exact match (all fields right) | 97.0% |
| `action` right | 98.0% |
| `unit` right | 99.0% |
| `to` right | 100.0% |
| Decision right | 100.0% |
| **Unsafe: acted when it should have checked** | **0 (0.0%)** |
| **Acted on the wrong command** | **0 (0.0%)** |
| Median time per command | 0.00 s |
| Slowest 5% | 0.00 s |

## Decisions (rows: right answer, columns: what the system did)

| | ACT | READ_BACK | ASK_AGAIN |
|---|---|---|---|
| **ACT** | 45 | 0 | 0 |
| **READ_BACK** | 0 | 25 | 0 |
| **ASK_AGAIN** | 0 | 0 | 30 |

## Exact match by kind

| Kind | Right | Of |
|---|---|---|
| correction | 9 | 9 |
| handwritten | 9 | 10 |
| move_busy | 3 | 3 |
| move_lookalike | 12 | 12 |
| move_no_place | 7 | 7 |
| move_ok | 20 | 20 |
| move_unknown | 16 | 16 |
| park | 7 | 7 |
| release | 4 | 4 |
| status | 10 | 10 |
| unclear | 0 | 2 |

## First 3 mistakes

| Said | Expected | Got |
|---|---|---|
| take it over there | `{"action": null, "unit": null, "to": null}` | `{"action": "move", "unit": null, "to": null}` |
| move that trailer | `{"action": null, "unit": null, "to": null}` | `{"action": "move", "unit": null, "to": null}` |
| 4471 to door 6 and then, actually, leave it | `{"action": null, "unit": null, "to": null}` | `{"action": null, "unit": "4471", "to": null}` |
