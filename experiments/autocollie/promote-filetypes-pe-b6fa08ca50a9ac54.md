# Promote REJECTED — `b6fa08ca50a9ac54` on `filetypes/pe`

Generated 2026-05-25T19:07:47Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T19-03-17_20260525T190315-promote-b6fa08ca50a9ac54_azoth-validate.log; tail: calibration complete; computing per-filetype metrics
filetypes/pyproject.toml: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54
staged runtime azoth bundle: /tmp/tmp.IpQsXCzxxy
azoth bundle ok: /tmp/tmp.IpQsXCzxxy
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 64 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.30pp (10.02% → 11.33%)
  elf: L3 hostile ensemble recall +0.70pp (92.79% → 93.49%)
  javascript: L3 hostile ensemble recall +5.92pp (66.20% → 72.12%)
  package.json: L3 hostile ensemble recall +4.25pp (86.78% → 91.03%)
  xml: L3 hostile ensemble recall +6.16pp (2.74% → 8.90%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.28pp (13.53% → 13.82%)
  elf :: filetypes/elf recall@3FP/M +3.40pp (93.40% → 96.81%)
  go :: filetypes/go recall@3FP/M +0.34pp (4.84% → 5.18%)
  javascript :: filetypes/javascript recall@3FP/M +11.24pp (65.71% → 76.95%)
  package.json :: filegroups/config recall@3FP/M +0.83pp (98.71% → 99.54%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  pe :: filetypes/pe recall@3FP/M +13.87pp (61.35% → 75.22%)
  xml :: filegroups/config recall@3FP/M +12.33pp (3.42% → 15.75%)

4 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.30pp above LWM (10.02% → 11.33%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + package.json: L3 hostile ensemble recall +4.25pp above LWM (86.78% → 91.03%)
  + xml: L3 hostile ensemble recall +6.16pp above LWM (2.74% → 8.90%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - pe: L3 hostile ENSEMBLE recall dropped 3.21pp BELOW LOW-WATER-MARK (61.96% → 58.74%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b6fa08ca50a9ac54` | `96a4083ae34b084c` | `7b8a38aeb675012b` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9999 | 0.9999 |
| F1 | 0.9918 | 0.9989 | 0.9978 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-25T19-03-17_20260525T190315-promote-b6fa08ca50a9ac54_azoth-validate.log; tail: calibration complete; computing per-filetype metrics
filetypes/pyproject.toml: 0 rows in score table; skipping
filetypes/xlsb: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-pe-b6fa08ca50a9ac54
staged runtime azoth bundle: /tmp/tmp.IpQsXCzxxy
azoth bundle ok: /tmp/tmp.IpQsXCzxxy
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 64 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +1.30pp (10.02% → 11.33%)
  elf: L3 hostile ensemble recall +0.70pp (92.79% → 93.49%)
  javascript: L3 hostile ensemble recall +5.92pp (66.20% → 72.12%)
  package.json: L3 hostile ensemble recall +4.25pp (86.78% → 91.03%)
  xml: L3 hostile ensemble recall +6.16pp (2.74% → 8.90%)

per-route improvements (≥0.10pp, informational):
  c :: filetypes/c recall@3FP/M +0.28pp (13.53% → 13.82%)
  elf :: filetypes/elf recall@3FP/M +3.40pp (93.40% → 96.81%)
  go :: filetypes/go recall@3FP/M +0.34pp (4.84% → 5.18%)
  javascript :: filetypes/javascript recall@3FP/M +11.24pp (65.71% → 76.95%)
  package.json :: filegroups/config recall@3FP/M +0.83pp (98.71% → 99.54%)
  package.json :: filetypes/package.json recall@3FP/M +1.02pp (98.66% → 99.68%)
  pe :: filetypes/pe recall@3FP/M +13.87pp (61.35% → 75.22%)
  xml :: filegroups/config recall@3FP/M +12.33pp (3.42% → 15.75%)

4 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +1.30pp above LWM (10.02% → 11.33%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + package.json: L3 hostile ensemble recall +4.25pp above LWM (86.78% → 91.03%)
  + xml: L3 hostile ensemble recall +6.16pp above LWM (2.74% → 8.90%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - pe: L3 hostile ENSEMBLE recall dropped 3.21pp BELOW LOW-WATER-MARK (61.96% → 58.74%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 2 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
