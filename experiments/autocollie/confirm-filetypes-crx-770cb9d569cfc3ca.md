# Confirm PASS — 770cb9d569cfc3ca on `filetypes/crx`

Cycle `20260628T102950-confirm-770cb9d569cfc3ca` — 2026-06-28T10:29:50Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `770cb9d569cfc3ca` | `66299a7423dfa9db` | `66299a7423dfa9db` | `66299a7423dfa9db` |
| PR AUC | 0.9966 | 0.9946 | 0.9944 | 0.9952 |
| ROC AUC | 0.9966 | 0.9946 | 0.9942 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=770cb9d569cfc3ca
```
