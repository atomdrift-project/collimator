# Promote REJECTED — `69a0ff2f47fb496a` on `filetypes/deb`

Generated 2026-10-31T00:59:21Z

azoth-validate failed: signal: terminated (log /home/t/src/collimator/out/autocollie/runs/2026-10-31T00-54-34_20261031T005347-promote-69a0ff2f47fb496a_azoth-validate.log; tail: 	--db postgres://hopper@localhost:5432/hopper --azoth-root /home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a --summary /home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/specialists.json \
	--general-scores /home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general/threshold_scores.npz --partition dev \
	 --check-inputs-only
.venv/bin/python -m collimator tune-thresholds \
	--db postgres://hopper@localhost:5432/hopper \
	--model "/home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general" --scores-only \
	--spec "/home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general/feature_spec.json" \
	 \
	--workers 12 \
	--scores-cache "/home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general/threshold_scores.npz" \
	--output "/home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general/threshold_tuning.json"
20:54:35 INFO  collimator.thresholds._inspect: building threshold score cache at /home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general/threshold_scores.npz
20:54:35 INFO  collimator.model: ONNX input projection: 127227 -> 8116 columns across 3 members
20:55:06 INFO  collimator.thresholds._inspect: threshold metadata progress: 4500000 rows, 30.7s elapsed
20:55:37 INFO  collimator.thresholds._inspect: threshold metadata progress: 9200000 rows, 61.3s elapsed
20:56:07 INFO  collimator.thresholds._inspect: threshold metadata progress: 14100000 rows, 91.9s elapsed
20:56:39 INFO  collimator.thresholds._inspect: threshold metadata progress: 16400000 rows, 123.2s elapsed
20:57:09 INFO  collimator.thresholds._inspect: threshold metadata progress: 18000000 rows, 153.7s elapsed
20:57:40 INFO  collimator.thresholds._inspect: threshold metadata progress: 19400000 rows, 184.5s elapsed
20:58:03 INFO  collimator.thresholds._inspect: threshold scoring metadata: 21393691 labeled rows in 207.9s
20:58:04 INFO  collimator.features: unordered DB-backed feature extraction: 21393691 rows, 12 workers, batch_size=341
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
20:58:21 INFO  collimator.thresholds._inspect: threshold scoring progress: 100254/21393691 rows (0.5%, 5650 rows/sec)
20:58:21 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=49.2s extract=90.5s; parent matrix=0.5s predict=1.9s
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
20:58:31 INFO  collimator.thresholds._inspect: threshold scoring progress: 200508/21393691 rows (0.9%, 7253 rows/sec)
20:58:31 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=89.8s extract=167.6s; parent matrix=0.9s predict=3.5s
20:58:40 INFO  collimator.thresholds._inspect: threshold scoring progress: 300762/21393691 rows (1.4%, 8153 rows/sec)
20:58:40 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=128.0s extract=233.4s; parent matrix=1.3s predict=5.3s
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
20:58:48 INFO  collimator.thresholds._inspect: threshold scoring progress: 401016/21393691 rows (1.9%, 8970 rows/sec)
20:58:48 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=162.3s extract=292.2s; parent matrix=1.6s predict=6.9s
20:58:56 INFO  collimator.thresholds._inspect: threshold scoring progress: 501270/21393691 rows (2.3%, 9555 rows/sec)
20:58:56 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=196.7s extract=347.4s; parent matrix=2.0s predict=8.6s
20:59:03 INFO  collimator.thresholds._inspect: threshold scoring progress: 601524/21393691 rows (2.8%, 10094 rows/sec)
20:59:03 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=222.8s extract=402.8s; parent matrix=2.3s predict=10.4s
20:59:12 INFO  collimator.thresholds._inspect: threshold scoring progress: 701778/21393691 rows (3.3%, 10199 rows/sec)
20:59:12 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=263.8s extract=469.1s; parent matrix=2.6s predict=12.3s
20:59:19 INFO  collimator.thresholds._inspect: threshold scoring progress: 802032/21393691 rows (3.7%, 10642 rows/sec)
20:59:19 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=288.2s extract=523.8s; parent matrix=2.9s predict=14.0s
make: *** [Makefile:1251: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.1093 -> 0.2093; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `69a0ff2f47fb496a` | `eff1e47ed6231660` | `f304fe5e7f664426` |
| PR AUC | 0.1093 | 0.2093 | 0.1946 |
| ROC AUC | 0.6579 | 0.8657 | 0.8550 |
| F1 | 0.1250 | 0.3158 | 0.2963 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/src/collimator/out/autocollie/runs/2026-10-31T00-54-34_20261031T005347-promote-69a0ff2f47fb496a_azoth-validate.log; tail: 	--db postgres://hopper@localhost:5432/hopper --azoth-root /home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a --summary /home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/specialists.json \
	--general-scores /home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general/threshold_scores.npz --partition dev \
	 --check-inputs-only
.venv/bin/python -m collimator tune-thresholds \
	--db postgres://hopper@localhost:5432/hopper \
	--model "/home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general" --scores-only \
	--spec "/home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general/feature_spec.json" \
	 \
	--workers 12 \
	--scores-cache "/home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general/threshold_scores.npz" \
	--output "/home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general/threshold_tuning.json"
20:54:35 INFO  collimator.thresholds._inspect: building threshold score cache at /home/t/src/collimator/out/models/azoth-candidate-filetypes-deb-69a0ff2f47fb496a/general/threshold_scores.npz
20:54:35 INFO  collimator.model: ONNX input projection: 127227 -> 8116 columns across 3 members
20:55:06 INFO  collimator.thresholds._inspect: threshold metadata progress: 4500000 rows, 30.7s elapsed
20:55:37 INFO  collimator.thresholds._inspect: threshold metadata progress: 9200000 rows, 61.3s elapsed
20:56:07 INFO  collimator.thresholds._inspect: threshold metadata progress: 14100000 rows, 91.9s elapsed
20:56:39 INFO  collimator.thresholds._inspect: threshold metadata progress: 16400000 rows, 123.2s elapsed
20:57:09 INFO  collimator.thresholds._inspect: threshold metadata progress: 18000000 rows, 153.7s elapsed
20:57:40 INFO  collimator.thresholds._inspect: threshold metadata progress: 19400000 rows, 184.5s elapsed
20:58:03 INFO  collimator.thresholds._inspect: threshold scoring metadata: 21393691 labeled rows in 207.9s
20:58:04 INFO  collimator.features: unordered DB-backed feature extraction: 21393691 rows, 12 workers, batch_size=341
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
20:58:21 INFO  collimator.thresholds._inspect: threshold scoring progress: 100254/21393691 rows (0.5%, 5650 rows/sec)
20:58:21 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=49.2s extract=90.5s; parent matrix=0.5s predict=1.9s
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
20:58:31 INFO  collimator.thresholds._inspect: threshold scoring progress: 200508/21393691 rows (0.9%, 7253 rows/sec)
20:58:31 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=89.8s extract=167.6s; parent matrix=0.9s predict=3.5s
20:58:40 INFO  collimator.thresholds._inspect: threshold scoring progress: 300762/21393691 rows (1.4%, 8153 rows/sec)
20:58:40 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=128.0s extract=233.4s; parent matrix=1.3s predict=5.3s
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
20:58:48 INFO  collimator.thresholds._inspect: threshold scoring progress: 401016/21393691 rows (1.9%, 8970 rows/sec)
20:58:48 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=162.3s extract=292.2s; parent matrix=1.6s predict=6.9s
20:58:56 INFO  collimator.thresholds._inspect: threshold scoring progress: 501270/21393691 rows (2.3%, 9555 rows/sec)
20:58:56 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=196.7s extract=347.4s; parent matrix=2.0s predict=8.6s
20:59:03 INFO  collimator.thresholds._inspect: threshold scoring progress: 601524/21393691 rows (2.8%, 10094 rows/sec)
20:59:03 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=222.8s extract=402.8s; parent matrix=2.3s predict=10.4s
20:59:12 INFO  collimator.thresholds._inspect: threshold scoring progress: 701778/21393691 rows (3.3%, 10199 rows/sec)
20:59:12 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=263.8s extract=469.1s; parent matrix=2.6s predict=12.3s
20:59:19 INFO  collimator.thresholds._inspect: threshold scoring progress: 802032/21393691 rows (3.7%, 10642 rows/sec)
20:59:19 INFO  collimator.thresholds._inspect: threshold stage totals: worker fetch=288.2s extract=523.8s; parent matrix=2.9s predict=14.0s
make: *** [Makefile:1251: azoth-calibrate] Terminated)
