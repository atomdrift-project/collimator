# Promote REJECTED — `b660c4e4d0bea14d` on `filegroups/source`

Generated 2026-05-25T18:40:28Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T18-35-29_20260525T183526-promote-b660c4e4d0bea14d_azoth-validate.log; tail: 	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d
staged runtime azoth bundle: /tmp/tmp.7pMaDZl1qO
azoth bundle ok: /tmp/tmp.7pMaDZl1qO
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 58 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.38pp (10.02% → 12.40%)
  elf: L3 hostile ensemble recall +0.70pp (92.79% → 93.49%)
  javascript: L3 hostile ensemble recall +9.33pp (66.20% → 75.53%)
  kotlin: L3 hostile ensemble recall +5.24pp (52.67% → 57.91%)
  package.json: L3 hostile ensemble recall +4.25pp (86.78% → 91.03%)
  rust: L3 hostile ensemble recall +0.61pp (1.22% → 1.83%)
  xml: L3 hostile ensemble recall +6.16pp (2.74% → 8.90%)

per-route improvements (≥0.10pp, informational):
  elf :: filetypes/elf recall@3FP/M +3.40pp (93.40% → 96.81%)
  go :: filetypes/go recall@3FP/M +0.59pp (4.84% → 5.44%)
  javascript :: filetypes/javascript recall@3FP/M +12.81pp (65.71% → 78.52%)
  package.json :: filegroups/config recall@3FP/M +0.83pp (98.71% → 99.54%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  xml :: filegroups/config recall@3FP/M +12.33pp (3.42% → 15.75%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 3.85pp (32.05% → 28.21%)
  kotlin :: filegroups/source recall@3FP/M dropped 8.23pp (72.06% → 63.83%)

5 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.38pp above LWM (10.02% → 12.40%)
  + javascript: L3 hostile ensemble recall +9.33pp above LWM (66.20% → 75.53%)
  + kotlin: L3 hostile ensemble recall +5.24pp above LWM (52.67% → 57.91%)
  + package.json: L3 hostile ensemble recall +4.25pp above LWM (86.78% → 91.03%)
  + xml: L3 hostile ensemble recall +6.16pp above LWM (2.74% → 8.90%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java: L3 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (50.00% → 25.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9988)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b660c4e4d0bea14d` | `7e9252b76aa81f4f` | `7565cc464d320091` |
| PR AUC | 0.9988 | 0.9991 | 0.9992 |
| ROC AUC | 0.9981 | 0.9984 | 0.9985 |
| F1 | 0.9830 | 0.9847 | 0.9800 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T18-35-29_20260525T183526-promote-b660c4e4d0bea14d_azoth-validate.log; tail: 	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-b660c4e4d0bea14d
staged runtime azoth bundle: /tmp/tmp.7pMaDZl1qO
azoth bundle ok: /tmp/tmp.7pMaDZl1qO
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 58 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.38pp (10.02% → 12.40%)
  elf: L3 hostile ensemble recall +0.70pp (92.79% → 93.49%)
  javascript: L3 hostile ensemble recall +9.33pp (66.20% → 75.53%)
  kotlin: L3 hostile ensemble recall +5.24pp (52.67% → 57.91%)
  package.json: L3 hostile ensemble recall +4.25pp (86.78% → 91.03%)
  rust: L3 hostile ensemble recall +0.61pp (1.22% → 1.83%)
  xml: L3 hostile ensemble recall +6.16pp (2.74% → 8.90%)

per-route improvements (≥0.10pp, informational):
  elf :: filetypes/elf recall@3FP/M +3.40pp (93.40% → 96.81%)
  go :: filetypes/go recall@3FP/M +0.59pp (4.84% → 5.44%)
  javascript :: filetypes/javascript recall@3FP/M +12.81pp (65.71% → 78.52%)
  package.json :: filegroups/config recall@3FP/M +0.83pp (98.71% → 99.54%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  xml :: filegroups/config recall@3FP/M +12.33pp (3.42% → 15.75%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 3.85pp (32.05% → 28.21%)
  kotlin :: filegroups/source recall@3FP/M dropped 8.23pp (72.06% → 63.83%)

5 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.38pp above LWM (10.02% → 12.40%)
  + javascript: L3 hostile ensemble recall +9.33pp above LWM (66.20% → 75.53%)
  + kotlin: L3 hostile ensemble recall +5.24pp above LWM (52.67% → 57.91%)
  + package.json: L3 hostile ensemble recall +4.25pp above LWM (86.78% → 91.03%)
  + xml: L3 hostile ensemble recall +6.16pp above LWM (2.74% → 8.90%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java: L3 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (50.00% → 25.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
