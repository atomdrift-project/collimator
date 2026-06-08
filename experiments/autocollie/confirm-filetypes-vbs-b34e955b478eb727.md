# Confirm PASS — b34e955b478eb727 on `filetypes/vbs`

Cycle `20260607T211010-confirm-b34e955b478eb727` — 2026-06-07T21:10:10Z

PR_AUC held across 3 seeds (orig 0.9977)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b34e955b478eb727` | `d50dcfca8ffb1647` | `d50dcfca8ffb1647` | `d50dcfca8ffb1647` |
| PR AUC | 0.9977 | 0.9976 | 0.9974 | 0.9974 |
| ROC AUC | 0.9922 | 0.9919 | 0.9912 | 0.9913 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b34e955b478eb727
```
