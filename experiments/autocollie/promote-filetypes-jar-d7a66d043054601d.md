# Promote REJECTED — `d7a66d043054601d` on `filetypes/jar`

Generated 2026-05-27T00:09:32Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-27T00-06-20_20260527T000601-promote-d7a66d043054601d_azoth-validate.log; tail: 	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-jar-d7a66d043054601d/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-jar-d7a66d043054601d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jar-d7a66d043054601d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jar-d7a66d043054601d/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jar-d7a66d043054601d
staged runtime azoth bundle: /tmp/tmp.WVR6Ju4Wni
azoth bundle ok: /tmp/tmp.WVR6Ju4Wni
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 65 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  jpeg: L3 hostile ensemble recall +10.94pp (1.56% → 12.50%)
  png: L3 hostile ensemble recall +4.72pp (4.26% → 8.98%)
  python: L3 hostile ensemble recall +0.48pp (66.33% → 66.81%)
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route improvements (≥0.10pp, informational):
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)
  jpeg :: filegroups/media recall@3FP/M +0.78pp (17.19% → 17.97%)

per-route regressions (informational; does not block deploy):
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

16 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + jpeg: L3 hostile ensemble recall +10.94pp above LWM (1.56% → 12.50%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.91pp above LWM (1.07% → 8.98%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.54pp above LWM (64.28% → 66.81%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - jar: L3 hostile ENSEMBLE recall dropped 4.69pp BELOW LOW-WATER-MARK (57.29% → 52.60%; LWM tolerance 0.90pp)

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
| key | `d7a66d043054601d` | `f56b005bb3223996` | `eee603089d437864` |
| PR AUC | 0.9987 | 0.9979 | 0.9984 |
| ROC AUC | 0.9975 | 0.9960 | 0.9971 |
| F1 | 0.9796 | 0.9722 | 0.9858 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-05-27T00-06-20_20260527T000601-promote-d7a66d043054601d_azoth-validate.log; tail: 	--output-md /home/t/collimator/out/models/azoth-candidate-filetypes-jar-d7a66d043054601d/route_policy_eval_oof.md \
	--output-json /home/t/collimator/out/models/azoth-candidate-filetypes-jar-d7a66d043054601d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jar-d7a66d043054601d/route_policy_eval_oof.json
wrote /home/t/collimator/out/models/azoth-candidate-filetypes-jar-d7a66d043054601d/route_policy_eval_oof.md
.venv/bin/python scripts/write_azoth_readmes.py --azoth-root /home/t/collimator/out/models/azoth-candidate-filetypes-jar-d7a66d043054601d
staged runtime azoth bundle: /tmp/tmp.WVR6Ju4Wni
azoth bundle ok: /tmp/tmp.WVR6Ju4Wni
--source-bundle out/models/azoth: 1 routes changed → 1 filetypes impacted, 65 unimpacted (drift treated as pre-existing)

ensemble improvements (≥0.10pp):
  jpeg: L3 hostile ensemble recall +10.94pp (1.56% → 12.50%)
  png: L3 hostile ensemble recall +4.72pp (4.26% → 8.98%)
  python: L3 hostile ensemble recall +0.48pp (66.33% → 66.81%)
  xls: L3 hostile ensemble recall +0.31pp (95.22% → 95.53%)

per-route improvements (≥0.10pp, informational):
  java_class :: filetypes/java_class recall@3FP/M +4.07pp (84.30% → 88.37%)
  jpeg :: filegroups/media recall@3FP/M +0.78pp (17.19% → 17.97%)

per-route regressions (informational; does not block deploy):
  perl :: filetypes/perl recall@3FP/M dropped 3.70pp (88.89% → 85.19%)
  xml :: filetypes/xml recall@3FP/M dropped 4.45pp (5.82% → 1.37%)

16 low-water-mark improvement(s) (>0.90pp above LWM, informational):
  + c: L3 hostile ensemble recall +2.72pp above LWM (10.02% → 12.74%)
  + java_class: L3 hostile ensemble recall +2.89pp above LWM (73.41% → 76.30%)
  + javascript: L3 hostile ensemble recall +8.35pp above LWM (66.20% → 74.55%)
  + jpeg: L3 hostile ensemble recall +10.94pp above LWM (1.56% → 12.50%)
  + lnk: L3 hostile ensemble recall +13.03pp above LWM (48.66% → 61.69%)
  + package.json: L3 hostile ensemble recall +3.79pp above LWM (86.78% → 90.57%)
  + pdf: L3 hostile ensemble recall +1.09pp above LWM (6.41% → 7.50%)
  + pe: L3 hostile ensemble recall +2.21pp above LWM (61.96% → 64.17%)
  + perl: L3 hostile ensemble recall +3.70pp above LWM (77.78% → 81.48%)
  + plist: L3 hostile ensemble recall +1.47pp above LWM (2.94% → 4.41%)
  + png: L3 hostile ensemble recall +7.91pp above LWM (1.07% → 8.98%)
  + powershell: L3 hostile ensemble recall +1.54pp above LWM (29.62% → 31.15%)
  + pptx: L3 hostile ensemble recall +9.09pp above LWM (9.09% → 18.18%)
  + python: L3 hostile ensemble recall +2.54pp above LWM (64.28% → 66.81%)
  + xls: L3 hostile ensemble recall +3.08pp above LWM (92.44% → 95.53%)
  + xml: L3 hostile ensemble recall +4.11pp above LWM (2.74% → 6.85%)

1 LOW-WATER-MARK regression(s) (pinned reference: out/models/azoth_low_water_mark/route_policy_eval_oof.json):
  - jar: L3 hostile ENSEMBLE recall dropped 4.69pp BELOW LOW-WATER-MARK (57.29% → 52.60%; LWM tolerance 0.90pp)

compared 63 filetypes (mal≥1, ben≥1); 3 below threshold and skipped.

blocked by: low-water-mark gate (0.90pp vs out/models/azoth_low_water_mark/route_policy_eval_oof.json)

If this regression is intentional, set AZOTH_ALLOW_REGRESSION=1 and re-run (or pass --net-improvement-fallback for shared-route promotes to address the deployed-tolerance gate only — the LWM gate is unconditional and AZOTH_ALLOW_REGRESSION is the only override for it).
make[2]: *** [Makefile:1136: azoth-validate] Error 1)
