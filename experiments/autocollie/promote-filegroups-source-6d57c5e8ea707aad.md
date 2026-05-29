# Promote REJECTED — `6d57c5e8ea707aad` on `filegroups/source`

Generated 2026-05-26T03:13:09Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T03-07-14_20260526T030611-promote-6d57c5e8ea707aad_azoth-validate.log; tail: 	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad
staged runtime azoth bundle: /tmp/tmp.HO8BZd0gLk
azoth bundle ok: /tmp/tmp.HO8BZd0gLk
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 59 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.79pp (11.33% → 12.12%)
  kotlin: L3 hostile ensemble recall +4.44pp (52.67% → 57.11%)

per-route improvements (≥0.10pp, informational):
  go :: filegroups/source recall@3FP/M +4.59pp (2.29% → 6.88%)
  rust :: filegroups/source recall@3FP/M +1.22pp (3.05% → 4.27%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 3.85pp (32.05% → 28.21%)
  kotlin :: filegroups/source recall@3FP/M dropped 7.79pp (72.06% → 64.28%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.10pp above LWM (10.02% → 12.12%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + kotlin: L3 hostile ensemble recall +4.44pp above LWM (52.67% → 57.11%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java: L3 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (50.00% → 25.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9983)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6d57c5e8ea707aad` | `c86e76f095d74d24` | `d216c8624d66579d` |
| PR AUC | 0.9983 | 0.9988 | 0.9990 |
| ROC AUC | 0.9973 | 0.9978 | 0.9981 |
| F1 | 0.9772 | 0.9777 | 0.9795 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T03-07-14_20260526T030611-promote-6d57c5e8ea707aad_azoth-validate.log; tail: 	--score-table /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/score_table.npz \
	--general-scores /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/general/threshold_scores.npz \
	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-6d57c5e8ea707aad
staged runtime azoth bundle: /tmp/tmp.HO8BZd0gLk
azoth bundle ok: /tmp/tmp.HO8BZd0gLk
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 59 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.79pp (11.33% → 12.12%)
  kotlin: L3 hostile ensemble recall +4.44pp (52.67% → 57.11%)

per-route improvements (≥0.10pp, informational):
  go :: filegroups/source recall@3FP/M +4.59pp (2.29% → 6.88%)
  rust :: filegroups/source recall@3FP/M +1.22pp (3.05% → 4.27%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 3.85pp (32.05% → 28.21%)
  kotlin :: filegroups/source recall@3FP/M dropped 7.79pp (72.06% → 64.28%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.10pp above LWM (10.02% → 12.12%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + kotlin: L3 hostile ensemble recall +4.44pp above LWM (52.67% → 57.11%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +4.35pp above LWM (86.78% → 91.12%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + perl: L3 hostile ensemble recall +7.41pp above LWM (77.78% → 85.19%)
  + png: L3 hostile ensemble recall +3.20pp above LWM (1.07% → 4.26%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.05pp above LWM (64.28% → 66.33%)
  + xls: L3 hostile ensemble recall +2.78pp above LWM (92.44% → 95.22%)
  + xml: L3 hostile ensemble recall +8.22pp above LWM (2.74% → 10.96%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - java: L3 hostile ENSEMBLE recall dropped 25.00pp BELOW LOW-WATER-MARK (50.00% → 25.00%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
