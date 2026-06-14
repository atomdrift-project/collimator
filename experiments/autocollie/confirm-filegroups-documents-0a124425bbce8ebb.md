# Confirm PASS — 0a124425bbce8ebb on `filegroups/documents`

Cycle `20260614T005629-confirm-0a124425bbce8ebb` — 2026-06-14T00:56:29Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0a124425bbce8ebb` | `74a6a3835cc65a72` | `74a6a3835cc65a72` | `74a6a3835cc65a72` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0a124425bbce8ebb
```
