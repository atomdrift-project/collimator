# Confirm PASS — 16b8c171f03714c9 on `filetypes/rtf`

Cycle `20260527T073543-confirm-16b8c171f03714c9` — 2026-05-27T07:35:43Z

PR_AUC held across 3 seeds (orig 0.9780)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `16b8c171f03714c9` | `d62d73a20f958d8d` | `d62d73a20f958d8d` | `d62d73a20f958d8d` |
| PR AUC | 0.9780 | 0.9784 | 0.9784 | 0.9784 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=16b8c171f03714c9
```
