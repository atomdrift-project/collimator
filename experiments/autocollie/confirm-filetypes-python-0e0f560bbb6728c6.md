# Confirm PASS — 0e0f560bbb6728c6 on `filetypes/python`

Cycle `20260718T141635-confirm-0e0f560bbb6728c6` — 2026-07-18T14:16:35Z

PR_AUC held across 3 seeds (orig 0.9741)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0e0f560bbb6728c6` | `6696ca3297e96f72` | `6696ca3297e96f72` | `6696ca3297e96f72` |
| PR AUC | 0.9741 | 0.9783 | 0.9770 | 0.9778 |
| ROC AUC | 0.9882 | 0.9900 | 0.9890 | 0.9896 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0e0f560bbb6728c6
```
