# Promote REJECTED — `cd289d40b3f45d1f` on `filetypes/zip`

Generated 2026-05-25T21:01:00Z

AUC regressed at full-train: 0.9984 -> 0.9966

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `cd289d40b3f45d1f` | `35d7c92845e9f21d` | `82163de27a70dc21` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 |
| ROC AUC | 0.9984 | 0.9964 | 0.9966 |
| F1 | 0.9886 | 0.9952 | 0.9955 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9984 -> 0.9966
