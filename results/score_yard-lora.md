# yard-lora

100 test examples

| Measure | Result |
|---|---|
| Valid JSON | 100.0% |
| Exact match (all fields right) | 95.0% |
| `action` right | 97.0% |
| `unit` right | 98.0% |
| `to` right | 98.0% |
| Decision right | 98.0% |
| **Unsafe: acted when it should have checked** | **2 (2.0%)** |
| **Acted on the wrong command** | **2 (2.0%)** |
| Median time per command | 1.44 s |
| Slowest 5% | 1.68 s |

## Decisions (rows: right answer, columns: what the system did)

| | ACT | READ_BACK | ASK_AGAIN |
|---|---|---|---|
| **ACT** | 45 | 0 | 0 |
| **READ_BACK** | 0 | 25 | 0 |
| **ASK_AGAIN** | 2 | 0 | 28 |

## Exact match by kind

| Kind | Right | Of |
|---|---|---|
| correction | 9 | 9 |
| handwritten | 7 | 10 |
| move_busy | 3 | 3 |
| move_lookalike | 12 | 12 |
| move_no_place | 7 | 7 |
| move_ok | 20 | 20 |
| move_unknown | 16 | 16 |
| park | 7 | 7 |
| release | 4 | 4 |
| status | 10 | 10 |
| unclear | 0 | 2 |

## First 5 mistakes

| Said | Expected | Got |
|---|---|---|
| take it over there | `{"action": null, "unit": null, "to": null}` | `{"action": "move", "unit": null, "to": "staging"}` |
| move that trailer | `{"action": null, "unit": null, "to": null}` | `{"action": "move", "unit": null, "to": null}` |
| uh take forty four seventy one, no, forty four seventeen to door three | `{"action": "move", "unit": "4417", "to": "door_03"}` | `{"action": "move", "unit": "4471", "to": "door_03"}` |
| 4471 to door 6 and then, actually, leave it | `{"action": null, "unit": null, "to": null}` | `{"action": "status", "unit": "4471", "to": null}` |
| send the 1146 to door nine | `{"action": "move", "unit": "1146", "to": null}` | `{"action": "move", "unit": "1146", "to": "door_08"}` |
