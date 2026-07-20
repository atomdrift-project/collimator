# Confirm PASS — 11c9217a3fe2e095 on `filetypes/zip`

Cycle `20260713T061833-confirm-11c9217a3fe2e095` — 2026-07-13T06:18:33Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `11c9217a3fe2e095` | `c002171d54e0623d` | `c002171d54e0623d` | `c002171d54e0623d` |
| PR AUC | 0.9986 | 0.9990 | 0.9990 | 0.9989 |
| ROC AUC | 0.9940 | 0.9954 | 0.9955 | 0.9951 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=11c9217a3fe2e095
```
