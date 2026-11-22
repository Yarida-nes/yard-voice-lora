# qwen3-8b

100 test examples

| Measure | Result |
|---|---|
| Valid JSON | 100.0% |
| Exact match (all fields right) | 82.0% |
| `action` right | 93.0% |
| `unit` right | 96.0% |
| `to` right | 87.0% |
| Decision right | 87.0% |
| **Unsafe: acted when it should have checked** | **6 (6.0%)** |
| **Acted on the wrong command** | **8 (8.0%)** |
| Median time per command | 2.50 s |
| Slowest 5% | 2.83 s |

## Decisions (rows: right answer, columns: what the system did)

| | ACT | READ_BACK | ASK_AGAIN |
|---|---|---|---|
| **ACT** | 41 | 1 | 3 |
| **READ_BACK** | 0 | 25 | 0 |
| **ASK_AGAIN** | 6 | 3 | 21 |

## Exact match by kind

| Kind | Right | Of |
|---|---|---|
| correction | 9 | 9 |
| handwritten | 8 | 10 |
| move_busy | 3 | 3 |
| move_lookalike | 12 | 12 |
| move_no_place | 0 | 7 |
| move_ok | 18 | 20 |
| move_unknown | 15 | 16 |
| park | 7 | 7 |
| release | 4 | 4 |
| status | 6 | 10 |
| unclear | 0 | 2 |

## First 15 mistakes

| Said | Expected | Got |
|---|---|---|
| take it over there | `{"action": null, "unit": null, "to": null}` | `{"action": "move", "unit": null, "to": "staging"}` |
| 6188 needs moving please | `{"action": "move", "unit": "6188", "to": null}` | `{"action": "move", "unit": "6188", "to": "staging"}` |
| can you shift 6188 when you can | `{"action": "move", "unit": "6188", "to": null}` | `{"action": "move", "unit": "6188", "to": "staging"}` |
| where's fifty-five twenty-seven | `{"action": "status", "unit": "5527", "to": null}` | `{"action": "status", "unit": null, "to": null}` |
| move 5527 please | `{"action": "move", "unit": "5527", "to": null}` | `{"action": "move", "unit": "5527", "to": "staging"}` |
| where's five zero three two when you can | `{"action": "status", "unit": "5032", "to": null}` | `{"action": "status", "unit": null, "to": null}` |
| has 4417 been moved mate | `{"action": "status", "unit": "4417", "to": null}` | `{"action": "move", "unit": "4417", "to": "door_01"}` |
| right, can you shift three three six four | `{"action": "move", "unit": "3364", "to": null}` | `{"action": "move", "unit": "3364", "to": "staging"}` |
| can you shift seventy-one forty mate | `{"action": "move", "unit": "7140", "to": null}` | `{"action": "move", "unit": "7140", "to": "door_01"}` |
| okay, take 5032 over mate | `{"action": "move", "unit": "5032", "to": null}` | `{"action": "move", "unit": "5032", "to": "door_01"}` |
| um, can you put fifty thirty-two on door seven thanks | `{"action": "move", "unit": "5032", "to": "door_07"}` | `{"action": "move", "unit": "532", "to": "door_07"}` |
| move that trailer | `{"action": null, "unit": null, "to": null}` | `{"action": "move", "unit": null, "to": null}` |
| yeah, take 2296 over | `{"action": "move", "unit": "2296", "to": null}` | `{"action": "move", "unit": "2296", "to": "staging"}` |
| yeah, 1957, dock door four mate | `{"action": "move", "unit": "1957", "to": "door_04"}` | `{"action": "park", "unit": "1957", "to": "door_04"}` |
| yeah, has forty-eight ninety-two been moved | `{"action": "status", "unit": "4892", "to": null}` | `{"action": "move", "unit": "4892", "to": "door_01"}` |
