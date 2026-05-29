# Promote REJECTED — `a5215de4aee3d9d4` on `filetypes/shell`

Generated 2026-05-27T01:04:25Z

AUC regressed at full-train: 0.9996 -> 0.9981

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9986)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a5215de4aee3d9d4` | `0e418aa7e6d885e1` | `ed91cb814b2e36b9` |
| PR AUC | 0.9986 | 0.9972 | 0.9972 |
| ROC AUC | 0.9996 | 0.9981 | 0.9981 |
| F1 | 0.9755 | 0.9723 | 0.9702 |

## Disposition

This spec did not survive the promotion ladder.

AUC regressed at full-train: 0.9996 -> 0.9981
