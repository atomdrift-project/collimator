# Promote REJECTED — `39e529347cd04596` on `filetypes/static-lib`

Generated 2026-10-29T11:19:55Z

azoth-validate failed: signal: terminated (log /home/t/src/collimator/out/autocollie/runs/2026-10-29T03-44-30_20261029T034414-promote-39e529347cd04596_azoth-validate.log; tail: 2026-10-29 03:06:48,371 INFO collimator.model: ONNX input projection: 6825 -> 545 columns across 3 members
2026-10-29 03:06:49,582 INFO collimator.features: DB-backed feature extraction: 1845690 rows, 1 workers, batch_size=1024
2026-10-29 03:06:52,637 WARNING collimator.features: fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
2026-10-29 03:07:22,476 WARNING collimator.features: fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
2026-10-29 03:07:38,976 WARNING collimator.features: fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
2026-10-29 03:37:01,863 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 3s (6881s of 7200s budget left)
2026-10-29 04:00:40,743 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 2s (7037s of 7200s budget left)
2026-10-29 04:00:41,138 WARNING collimator.data: psycopg connect failed (attempt 2): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 6s (5461s of 7200s budget left)
2026-10-29 04:00:41,131 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 3s (6821s of 7200s budget left)
2026-10-29 04:00:42,558 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 3s (6761s of 7200s budget left)
2026-10-29 04:14:20,511 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 3s (6719s of 7200s budget left)
2026-10-29 04:14:20,512 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 3s (6861s of 7200s budget left)
2026-10-29 04:14:25,523 WARNING collimator.data: psycopg connect failed (attempt 1): connection failed: connection to server at "127.0.0.1", port 5432 failed: server closed the connection unexpectedly
	This probably means the server terminated abnormally
	before or while processing the request.
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: server closed the connection unexpectedly
	This probably means the server terminated abnormally
	before or while processing the request. — retrying in 2s (7102s of 7200s budget left)
make[1]: *** [Makefile:1237: azoth-calibrate] Terminated)

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.5912)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `39e529347cd04596` | `d98fd3fe57bdc91b` | `f00dc42aa58b1ad7` |
| PR AUC | 0.5912 | 0.6202 | 0.6139 |
| ROC AUC | 0.8767 | 0.9016 | 0.8971 |
| F1 | 0.1882 | 0.6176 | 0.6005 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/src/collimator/out/autocollie/runs/2026-10-29T03-44-30_20261029T034414-promote-39e529347cd04596_azoth-validate.log; tail: 2026-10-29 03:06:48,371 INFO collimator.model: ONNX input projection: 6825 -> 545 columns across 3 members
2026-10-29 03:06:49,582 INFO collimator.features: DB-backed feature extraction: 1845690 rows, 1 workers, batch_size=1024
2026-10-29 03:06:52,637 WARNING collimator.features: fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
2026-10-29 03:07:22,476 WARNING collimator.features: fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
2026-10-29 03:07:38,976 WARNING collimator.features: fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
2026-10-29 03:37:01,863 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 3s (6881s of 7200s budget left)
2026-10-29 04:00:40,743 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 2s (7037s of 7200s budget left)
2026-10-29 04:00:41,138 WARNING collimator.data: psycopg connect failed (attempt 2): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 6s (5461s of 7200s budget left)
2026-10-29 04:00:41,131 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 3s (6821s of 7200s budget left)
2026-10-29 04:00:42,558 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 3s (6761s of 7200s budget left)
2026-10-29 04:14:20,511 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 3s (6719s of 7200s budget left)
2026-10-29 04:14:20,512 WARNING collimator.data: psycopg connect failed (attempt 1): connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection timeout expired — retrying in 3s (6861s of 7200s budget left)
2026-10-29 04:14:25,523 WARNING collimator.data: psycopg connect failed (attempt 1): connection failed: connection to server at "127.0.0.1", port 5432 failed: server closed the connection unexpectedly
	This probably means the server terminated abnormally
	before or while processing the request.
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: server closed the connection unexpectedly
	This probably means the server terminated abnormally
	before or while processing the request. — retrying in 2s (7102s of 7200s budget left)
make[1]: *** [Makefile:1237: azoth-calibrate] Terminated)
