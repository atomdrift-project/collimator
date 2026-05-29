# Promote REJECTED — `38764087b23c3273` on `filegroups/config`

Generated 2026-05-26T15:05:45Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T14-59-24_20260526T145838-promote-38764087b23c3273_azoth-validate.log; tail: filetypes/pyproject.toml: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273
staged runtime azoth bundle: /tmp/tmp.601ZIYG3sr
azoth bundle ok: /tmp/tmp.601ZIYG3sr
--source-bundle out/models/azoth: 1 routes changed → 3 filetypes impacted, 63 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  elf: L3 hostile ensemble recall +3.94pp (92.05% → 95.99%)
  pe: L3 hostile ensemble recall +1.46pp (62.71% → 64.17%)

per-route improvements (≥0.10pp, informational):
  elf :: filegroups/native recall@3FP/M +10.64pp (86.66% → 97.29%)
  macho :: filegroups/native recall@3FP/M +4.96pp (69.08% → 74.05%)

per-route regressions (informational; does not block deploy):
  xml :: filegroups/config recall@3FP/M dropped 5.82pp (11.30% → 5.48%)

15 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + elf: L3 hostile ensemble recall +3.20pp above LWM (92.79% → 95.99%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.25pp above LWM (86.78% → 91.03%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +4.45pp above LWM (2.74% → 7.19%)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9997)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `38764087b23c3273` | `9b5b8d89c6b742a4` | `a7670cb7e2e565ae` |
| PR AUC | 0.9997 | 0.9999 | 0.9999 |
| ROC AUC | 0.9995 | 0.9997 | 0.9997 |
| F1 | 0.9954 | 0.9946 | 0.9916 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T14-59-24_20260526T145838-promote-38764087b23c3273_azoth-validate.log; tail: filetypes/pyproject.toml: 0 rows in score table; skipping
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-config-38764087b23c3273
staged runtime azoth bundle: /tmp/tmp.601ZIYG3sr
azoth bundle ok: /tmp/tmp.601ZIYG3sr
--source-bundle out/models/azoth: 1 routes changed → 3 filetypes impacted, 63 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  elf: L3 hostile ensemble recall +3.94pp (92.05% → 95.99%)
  pe: L3 hostile ensemble recall +1.46pp (62.71% → 64.17%)

per-route improvements (≥0.10pp, informational):
  elf :: filegroups/native recall@3FP/M +10.64pp (86.66% → 97.29%)
  macho :: filegroups/native recall@3FP/M +4.96pp (69.08% → 74.05%)

per-route regressions (informational; does not block deploy):
  xml :: filegroups/config recall@3FP/M dropped 5.82pp (11.30% → 5.48%)

15 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + elf: L3 hostile ensemble recall +3.20pp above LWM (92.79% → 95.99%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.25pp above LWM (86.78% → 91.03%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +4.45pp above LWM (2.74% → 7.19%)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
