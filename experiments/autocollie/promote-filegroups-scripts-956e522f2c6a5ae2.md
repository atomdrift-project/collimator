# Promote REJECTED — `956e522f2c6a5ae2` on `filegroups/scripts`

Generated 2026-05-25T16:03:10Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T15-55-45_20260525T155542-promote-956e522f2c6a5ae2_azoth-validate.log; tail: filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2
staged runtime azoth bundle: /tmp/tmp.Ufmwsh53G8
azoth bundle ok: /tmp/tmp.Ufmwsh53G8
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 56 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  javascript: L3 hostile ensemble recall +2.31pp (66.20% → 68.50%)
  perl: L3 hostile ensemble recall +3.70pp (77.78% → 81.48%)
  powershell: L3 hostile ensemble recall +1.15pp (29.62% → 30.77%)
  shell: L3 hostile ensemble recall +0.37pp (82.78% → 83.15%)

per-route improvements (≥0.10pp, informational):
  perl :: filegroups/scripts recall@3FP/M +3.70pp (85.19% → 88.89%)
  php :: filegroups/scripts recall@3FP/M +0.78pp (66.60% → 67.38%)
  powershell :: filegroups/scripts recall@3FP/M +10.77pp (51.15% → 61.92%)
  python :: filegroups/scripts recall@3FP/M +4.52pp (63.40% → 67.91%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 97.62pp (99.01% → 1.39%)
  javascript :: filegroups/scripts recall@3FP/M dropped 2.53pp (75.73% → 73.20%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)

4 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + javascript: L3 hostile ensemble recall +2.31pp above LWM (66.20% → 68.50%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + powershell: L3 hostile ensemble recall +1.15pp above LWM (29.62% → 30.77%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.87pp BELOW LOW-WATER-MARK (98.83% → 93.97%; LWM tolerance 0.90pp)
  - php: L3 hostile ENSEMBLE recall dropped 12.11pp BELOW LOW-WATER-MARK (62.11% → 50.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9981)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `956e522f2c6a5ae2` | `4b4b4b572ed39a36` | `abf6ebae61fbc009` |
| PR AUC | 0.9981 | 0.9993 | 0.9994 |
| ROC AUC | 0.9979 | 0.9992 | 0.9993 |
| F1 | 0.9787 | 0.9836 | 0.9834 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T15-55-45_20260525T155542-promote-956e522f2c6a5ae2_azoth-validate.log; tail: filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-956e522f2c6a5ae2
staged runtime azoth bundle: /tmp/tmp.Ufmwsh53G8
azoth bundle ok: /tmp/tmp.Ufmwsh53G8
--source-bundle out/models/azoth: 1 routes changed → 9 filetypes impacted, 56 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +2.49pp (10.02% → 12.51%)
  javascript: L3 hostile ensemble recall +2.31pp (66.20% → 68.50%)
  perl: L3 hostile ensemble recall +3.70pp (77.78% → 81.48%)
  powershell: L3 hostile ensemble recall +1.15pp (29.62% → 30.77%)
  shell: L3 hostile ensemble recall +0.37pp (82.78% → 83.15%)

per-route improvements (≥0.10pp, informational):
  perl :: filegroups/scripts recall@3FP/M +3.70pp (85.19% → 88.89%)
  php :: filegroups/scripts recall@3FP/M +0.78pp (66.60% → 67.38%)
  powershell :: filegroups/scripts recall@3FP/M +10.77pp (51.15% → 61.92%)
  python :: filegroups/scripts recall@3FP/M +4.52pp (63.40% → 67.91%)

per-route regressions (informational; does not block deploy):
  batch :: filegroups/scripts recall@3FP/M dropped 97.62pp (99.01% → 1.39%)
  javascript :: filegroups/scripts recall@3FP/M dropped 2.53pp (75.73% → 73.20%)
  lua :: filegroups/scripts recall@3FP/M dropped 16.67pp (66.67% → 50.00%)

4 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.49pp above LWM (10.02% → 12.51%)
  + javascript: L3 hostile ensemble recall +2.31pp above LWM (66.20% → 68.50%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + powershell: L3 hostile ensemble recall +1.15pp above LWM (29.62% → 30.77%)

2 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - batch: L3 hostile ENSEMBLE recall dropped 4.87pp BELOW LOW-WATER-MARK (98.83% → 93.97%; LWM tolerance 0.90pp)
  - php: L3 hostile ENSEMBLE recall dropped 12.11pp BELOW LOW-WATER-MARK (62.11% → 50.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
