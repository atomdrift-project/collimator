# Promote REJECTED — `b0d6f9295501a29b` on `filegroups/scripts`

Generated 2026-07-04T08:10:15Z

AUC regressed at full-train: 0.9976 -> 0.9964

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9978)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b0d6f9295501a29b` | `959624b4a3dde45f` | `41bf489d3e40daad` |
| PR AUC | 0.9978 | 0.9949 | 0.9954 |
| ROC AUC | 0.9976 | 0.9960 | 0.9964 |
| F1 | 0.9693 | 0.9514 | 0.9534 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9976 -> 0.9964
