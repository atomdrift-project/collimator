# Promote REJECTED — `b0756a90274b0c7a` on `filegroups/config`

Generated 2026-05-26T15:48:33Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T15-42-27_20260526T154143-promote-b0756a90274b0c7a_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a
staged runtime azoth bundle: /tmp/tmp.GUgeasFJZd
azoth bundle ok: /tmp/tmp.GUgeasFJZd
--source-bundle out/models/azoth: 1 routes changed → 3 filetypes impacted, 63 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  elf: L3 hostile ensemble recall +3.94pp (92.05% → 95.99%)
  package.json: L3 hostile ensemble recall +0.60pp (91.12% → 91.72%)
  pe: L3 hostile ensemble recall +1.46pp (62.71% → 64.17%)

per-route improvements (≥0.10pp, informational):
  elf :: filegroups/native recall@3FP/M +10.64pp (86.66% → 97.29%)
  macho :: filegroups/native recall@3FP/M +4.96pp (69.08% → 74.05%)

15 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + elf: L3 hostile ensemble recall +3.20pp above LWM (92.79% → 95.99%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.95pp above LWM (86.78% → 91.72%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +3.77pp above LWM (2.74% → 6.51%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - plist: L3 hostile ENSEMBLE recall dropped 1.47pp BELOW LOW-WATER-MARK (2.94% → 1.47%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9998)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b0756a90274b0c7a` | `5f1f831f446f53df` | `34032cf0834e00aa` |
| PR AUC | 0.9998 | 0.9999 | 0.9999 |
| ROC AUC | 0.9995 | 0.9998 | 0.9998 |
| F1 | 0.9959 | 0.9937 | 0.9939 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T15-42-27_20260526T154143-promote-b0756a90274b0c7a_azoth-validate.log; tail: wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/per_filetype_metrics.json (filetypes: 79, filegroups: 0)
.venv/bin/python scripts/azoth_route_policy_eval.py \
	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-config-b0756a90274b0c7a
staged runtime azoth bundle: /tmp/tmp.GUgeasFJZd
azoth bundle ok: /tmp/tmp.GUgeasFJZd
--source-bundle out/models/azoth: 1 routes changed → 3 filetypes impacted, 63 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  elf: L3 hostile ensemble recall +3.94pp (92.05% → 95.99%)
  package.json: L3 hostile ensemble recall +0.60pp (91.12% → 91.72%)
  pe: L3 hostile ensemble recall +1.46pp (62.71% → 64.17%)

per-route improvements (≥0.10pp, informational):
  elf :: filegroups/native recall@3FP/M +10.64pp (86.66% → 97.29%)
  macho :: filegroups/native recall@3FP/M +4.96pp (69.08% → 74.05%)

15 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + elf: L3 hostile ensemble recall +3.20pp above LWM (92.79% → 95.99%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.95pp above LWM (86.78% → 91.72%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +3.77pp above LWM (2.74% → 6.51%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - plist: L3 hostile ENSEMBLE recall dropped 1.47pp BELOW LOW-WATER-MARK (2.94% → 1.47%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: deployed-tolerance gate (1.70pp), low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
