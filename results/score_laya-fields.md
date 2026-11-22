# laya-fields

100 test examples

| Measure | Result |
|---|---|
| Valid JSON | 100.0% |
| Exact match (all fields right) | 74.0% |
| `action` right | 99.0% |
| `unit` right | 99.0% |
| `to` right | 74.0% |
| Decision right | 93.0% |
| **Unsafe: acted when it should have checked** | **3 (3.0%)** |
| **Acted on the wrong command** | **11 (11.0%)** |
| Median time per command | 0.10 s |
| Slowest 5% | 0.10 s |

## Decisions (rows: right answer, columns: what the system did)

| | ACT | READ_BACK | ASK_AGAIN |
|---|---|---|---|
| **ACT** | 43 | 0 | 2 |
| **READ_BACK** | 0 | 24 | 1 |
| **ASK_AGAIN** | 3 | 1 | 26 |

## Exact match by kind

| Kind | Right | Of |
|---|---|---|
| correction | 7 | 9 |
| handwritten | 5 | 10 |
| move_busy | 1 | 3 |
| move_lookalike | 7 | 12 |
| move_no_place | 7 | 7 |
| move_ok | 12 | 20 |
| move_unknown | 12 | 16 |
| park | 7 | 7 |
| release | 4 | 4 |
| status | 10 | 10 |
| unclear | 2 | 2 |

## First 15 mistakes

| Said | Expected | Got |
|---|---|---|
| bring 3851 up to door 4 mate | `{"action": "move", "unit": "3851", "to": "door_04"}` | `{"action": "move", "unit": "3851", "to": "door_03"}` |
| um, send 2580 to dock door two when you can | `{"action": "move", "unit": "2580", "to": "door_02"}` | `{"action": "move", "unit": "2580", "to": "door_01"}` |
| uh, send 5527 to dock 4 please | `{"action": "move", "unit": "5527", "to": "door_04"}` | `{"action": "move", "unit": "5527", "to": "door_03"}` |
| um, move 6188 to dock door 3 please | `{"action": "move", "unit": "6188", "to": "door_03"}` | `{"action": "move", "unit": "6188", "to": "door_08"}` |
| shift five four six five over to dock three please | `{"action": "move", "unit": "5465", "to": "door_03"}` | `{"action": "move", "unit": "5465", "to": "door_04"}` |
| shift 4471 over to door seven thanks | `{"action": "move", "unit": "4471", "to": "door_07"}` | `{"action": "move", "unit": "4471", "to": "door_06"}` |
| bring 2269 up to dock 8 thanks | `{"action": "move", "unit": "2269", "to": "door_08"}` | `{"action": "move", "unit": "2269", "to": "door_01"}` |
| take 6603 to dock two | `{"action": "move", "unit": "6603", "to": "door_02"}` | `{"action": "move", "unit": "6603", "to": "door_01"}` |
| right, take thirty-eight fifty-one to dock door four please | `{"action": "move", "unit": "3851", "to": "door_04"}` | `{"action": "move", "unit": "3851", "to": "door_02"}` |
| um, can you put fifty thirty-two on door seven thanks | `{"action": "move", "unit": "5032", "to": "door_07"}` | `{"action": "move", "unit": "5032", "to": "door_06"}` |
| can you put three eight five one on door 3 | `{"action": "move", "unit": "3851", "to": "door_03"}` | `{"action": "move", "unit": "3851", "to": "door_01"}` |
| move 8420, no, scratch that, six six zero three to door seven | `{"action": "move", "unit": "6603", "to": "door_07"}` | `{"action": "move", "unit": "6603", "to": "door_01"}` |
| can you put 4892 on dock door 7 | `{"action": "move", "unit": "4892", "to": "door_07"}` | `{"action": "move", "unit": "4892", "to": "door_08"}` |
| okay, move two two two nine to dock door three | `{"action": "move", "unit": "2229", "to": "door_03"}` | `{"action": "move", "unit": "2229", "to": "door_02"}` |
| um, take six six zero three to door seven please | `{"action": "move", "unit": "6603", "to": "door_07"}` | `{"action": "move", "unit": "6603", "to": "door_06"}` |
