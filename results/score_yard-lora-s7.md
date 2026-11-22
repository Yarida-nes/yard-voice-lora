# yard-lora-s7

100 test examples

| Measure | Result |
|---|---|
| Valid JSON | 100.0% |
| Exact match (all fields right) | 96.0% |
| `action` right | 97.0% |
| `unit` right | 99.0% |
| `to` right | 99.0% |
| Decision right | 98.0% |
| **Unsafe: acted when it should have checked** | **1 (1.0%)** |
| **Acted on the wrong command** | **1 (1.0%)** |
| Median time per command | 1.42 s |
| Slowest 5% | 1.51 s |

## Decisions (rows: right answer, columns: what the system did)

| | ACT | READ_BACK | ASK_AGAIN |
|---|---|---|---|
| **ACT** | 45 | 0 | 0 |
| **READ_BACK** | 0 | 25 | 0 |
| **ASK_AGAIN** | 1 | 1 | 28 |

## Exact match by kind

| Kind | Right | Of |
|---|---|---|
| correction | 9 | 9 |
| handwritten | 8 | 10 |
| move_busy | 3 | 3 |
| move_lookalike | 12 | 12 |
| move_no_place | 7 | 7 |
| move_ok | 20 | 20 |
| move_unknown | 16 | 16 |
| park | 7 | 7 |
| release | 4 | 4 |
| status | 10 | 10 |
| unclear | 0 | 2 |

## First 4 mistakes

| Said | Expected | Got |
|---|---|---|
| take it over there | `{"action": null, "unit": null, "to": null}` | `{"action": "move", "unit": null, "to": null}` |
| move that trailer | `{"action": null, "unit": null, "to": null}` | `{"action": "move", "unit": null, "to": null}` |
| 4471 to door 6 and then, actually, leave it | `{"action": null, "unit": null, "to": null}` | `{"action": "release", "unit": "4471", "to": null}` |
| send the 1146 to door nine | `{"action": "move", "unit": "1146", "to": null}` | `{"action": "move", "unit": "1146", "to": "door_08"}` |
