# Confirm PASS — 63b68ef8bfa8c343 on `filetypes/rust`

Cycle `20260507T142458-confirm-63b68ef8bfa8c343` — 2026-05-07T14:24:58Z

F1 held: 1.0000 -> 1.0000

| | original | candidate (different seed) |
|---|---|---|
| key | `63b68ef8bfa8c343` | `4a13038ad3047787` |
| idea | rust_training_capacity_boost | rust_training_capacity_boost_confirm_seed43 |
| F1 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 |
| AP | 0.0000 | 0.0000 |

## Next step

The held-out signal reproduced under a different seed. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=63b68ef8bfa8c343
```

*(promote target is V3, not yet implemented — this command will be added soon.)*
