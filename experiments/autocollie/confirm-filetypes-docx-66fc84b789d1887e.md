# Confirm PASS — 66fc84b789d1887e on `filetypes/docx`

Cycle `20260527T075000-confirm-66fc84b789d1887e` — 2026-05-27T07:50:00Z

PR_AUC held across 3 seeds (orig 0.9897)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `66fc84b789d1887e` | `de517a8eb14bc864` | `de517a8eb14bc864` | `de517a8eb14bc864` |
| PR AUC | 0.9897 | 0.9898 | 0.9898 | 0.9898 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=66fc84b789d1887e
```
