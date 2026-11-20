# Labelling rules

The model only pulls the command out of the sentence:

```json
{"action": "move", "unit": "4471", "to": "door_06"}
```

- `action`: `move`, `park`, `release` or `status`. `null` if you can't tell.
- `unit`: the trailer number as 4 digits, exactly as the worker said it, even if it isn't in the yard. `null` if none was said.
- `to`: `door_01` to `door_08` or `staging` for `move`; always `parking` for `park`; `null` for `release` and `status`, or if no place was said.
- If the worker corrects themselves ("4417, no wait, 4471"), use the last thing they said.

The decision is made by code (`src/rules.py`) from that JSON and `data/yard.json`, in this order:

| # | Rule | Decision |
|---|---|---|
| 1 | No action or no trailer number | ASK_AGAIN |
| 2 | Trailer isn't in the yard | ASK_AGAIN |
| 3 | `move` with no place | ASK_AGAIN |
| 4 | `move` to a busy door | ASK_AGAIN |
| 5 | `status` | ACT (it only reads) |
| 6 | `release` (the trailer leaves the site) | READ_BACK |
| 7 | The trailer has a look-alike number in the yard (4471 / 4417) | READ_BACK |
| 8 | Anything else | ACT |

Change these if you think they're wrong, but write the change here and regenerate the data, so the labels and the code always agree.
