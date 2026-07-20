# Confirm PASS — 7fb08166a0c9fdc9 on `filetypes/elf`

Cycle `20260711T101407-confirm-7fb08166a0c9fdc9` — 2026-07-11T10:14:07Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7fb08166a0c9fdc9` | `60049aa71da85cd9` | `60049aa71da85cd9` | `60049aa71da85cd9` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9998 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7fb08166a0c9fdc9
```
