# Promote REJECTED — `40bfba6a7c77f2f8` on `filegroups/source`

Generated 2026-05-26T02:57:29Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T02-52-13_20260526T025207-promote-40bfba6a7c77f2f8_azoth-validate.log; tail: 	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8
staged runtime azoth bundle: /tmp/tmp.mjegGuTeyO
azoth bundle ok: /tmp/tmp.mjegGuTeyO
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 59 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.74pp (11.33% → 12.06%)
  go: L3 hostile ensemble recall +0.25pp (1.27% → 1.53%)
  kotlin: L3 hostile ensemble recall +4.86pp (52.67% → 57.53%)
  rust: L3 hostile ensemble recall +0.61pp (1.22% → 1.83%)

per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +0.51pp (13.36% → 13.87%)
  rust :: filegroups/source recall@3FP/M +1.22pp (3.05% → 4.27%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 3.42pp (32.05% → 28.63%)
  kotlin :: filegroups/source recall@3FP/M dropped 8.34pp (72.06% → 63.73%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.04pp above LWM (10.02% → 12.06%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + kotlin: L3 hostile ensemble recall +4.86pp above LWM (52.67% → 57.53%)
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

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9987)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `40bfba6a7c77f2f8` | `758b3d7304b3fdc6` | `ebc1c4fe04dea7b5` |
| PR AUC | 0.9987 | 0.9991 | 0.9991 |
| ROC AUC | 0.9980 | 0.9983 | 0.9984 |
| F1 | 0.9800 | 0.9807 | 0.9816 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-26T02-52-13_20260526T025207-promote-40bfba6a7c77f2f8_azoth-validate.log; tail: 	--route-policies /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/route_policies.json \
	--partition test \
	--output-md /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filegroups-source-40bfba6a7c77f2f8
staged runtime azoth bundle: /tmp/tmp.mjegGuTeyO
azoth bundle ok: /tmp/tmp.mjegGuTeyO
--source-bundle out/models/azoth: 1 routes changed → 7 filetypes impacted, 59 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  c: L3 hostile ensemble recall +0.74pp (11.33% → 12.06%)
  go: L3 hostile ensemble recall +0.25pp (1.27% → 1.53%)
  kotlin: L3 hostile ensemble recall +4.86pp (52.67% → 57.53%)
  rust: L3 hostile ensemble recall +0.61pp (1.22% → 1.83%)

per-route improvements (≥0.10pp, informational):
  c :: filegroups/source recall@3FP/M +0.51pp (13.36% → 13.87%)
  rust :: filegroups/source recall@3FP/M +1.22pp (3.05% → 4.27%)

per-route regressions (informational; does not block deploy):
  csharp :: filegroups/source recall@3FP/M dropped 3.42pp (32.05% → 28.63%)
  kotlin :: filegroups/source recall@3FP/M dropped 8.34pp (72.06% → 63.73%)

14 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.04pp above LWM (10.02% → 12.06%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +5.92pp above LWM (66.20% → 72.12%)
  + kotlin: L3 hostile ensemble recall +4.86pp above LWM (52.67% → 57.53%)
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
