# Promote REJECTED — `b0d6f9295501a29b` on `filegroups/scripts`

Generated 2026-05-25T15:55:39Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T15-48-40_20260525T154838-promote-b0d6f9295501a29b_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b
staged runtime azoth bundle: /tmp/tmp.Avv75H4klr
azoth bundle ok: /tmp/tmp.Avv75H4klr
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 56 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  javascript: L3 hostile ensemble recall +3.04pp (66.20% → 69.24%)
  perl: L3 hostile ensemble recall +3.70pp (77.78% → 81.48%)
  php: L3 hostile ensemble recall +0.20pp (62.11% → 62.30%)
  powershell: L3 hostile ensemble recall +2.31pp (29.62% → 31.92%)

per-route improvements (≥0.10pp, informational):
  javascript :: filegroups/scripts recall@3FP/M +0.34pp (75.73% → 76.07%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +8.08pp (51.15% → 59.23%)
  python :: filegroups/scripts recall@3FP/M +1.48pp (63.40% → 64.88%)
  shell :: filegroups/scripts recall@3FP/M +0.24pp (81.32% → 81.56%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.30pp (99.01% → 0.71%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 3.32pp (66.60% → 63.28%)

4 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + javascript: L3 hostile ensemble recall +3.04pp above LWM (66.20% → 69.24%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + powershell: L3 hostile ensemble recall +2.31pp above LWM (29.62% → 31.92%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.91pp BELOW LOW-WATER-MARK (98.83% → 93.92%; LWM tolerance 0.90pp)
  - python: L3 hostile ENSEMBLE recall dropped 1.36pp BELOW LOW-WATER-MARK (64.28% → 62.91%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9978)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b0d6f9295501a29b` | `fa6be051c8b0809c` | `3e6afabf181aab16` |
| PR AUC | 0.9978 | 0.9993 | 0.9993 |
| ROC AUC | 0.9976 | 0.9991 | 0.9992 |
| F1 | 0.9693 | 0.9840 | 0.9828 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T15-48-40_20260525T154838-promote-b0d6f9295501a29b_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-b0d6f9295501a29b
staged runtime azoth bundle: /tmp/tmp.Avv75H4klr
azoth bundle ok: /tmp/tmp.Avv75H4klr
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 56 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  javascript: L3 hostile ensemble recall +3.04pp (66.20% → 69.24%)
  perl: L3 hostile ensemble recall +3.70pp (77.78% → 81.48%)
  php: L3 hostile ensemble recall +0.20pp (62.11% → 62.30%)
  powershell: L3 hostile ensemble recall +2.31pp (29.62% → 31.92%)

per-route improvements (≥0.10pp, informational):
  javascript :: filegroups/scripts recall@3FP/M +0.34pp (75.73% → 76.07%)
  perl :: filegroups/scripts recall@3FP/M +7.41pp (85.19% → 92.59%)
  powershell :: filegroups/scripts recall@3FP/M +8.08pp (51.15% → 59.23%)
  python :: filegroups/scripts recall@3FP/M +1.48pp (63.40% → 64.88%)
  shell :: filegroups/scripts recall@3FP/M +0.24pp (81.32% → 81.56%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 98.30pp (99.01% → 0.71%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)
  php :: filegroups/scripts recall@3FP/M dropped 3.32pp (66.60% → 63.28%)

4 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + javascript: L3 hostile ensemble recall +3.04pp above LWM (66.20% → 69.24%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + powershell: L3 hostile ensemble recall +2.31pp above LWM (29.62% → 31.92%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.91pp BELOW LOW-WATER-MARK (98.83% → 93.92%; LWM tolerance 0.90pp)
  - python: L3 hostile ENSEMBLE recall dropped 1.36pp BELOW LOW-WATER-MARK (64.28% → 62.91%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
