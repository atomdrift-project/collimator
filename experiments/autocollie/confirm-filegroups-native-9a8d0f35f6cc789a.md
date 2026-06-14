# Confirm FAIL — 9a8d0f35f6cc789a on `filegroups/native`

Cycle `20260614T044950-confirm-9a8d0f35f6cc789a` — 2026-06-14T04:49:50Z

experiment failed: timed out after 30m0s (timeout(1) exit 124)
--- experiment log tail ---
...(truncated)...
 host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections? — retrying in 274s (6477s of 7200s budget left)
psycopg connect failed (attempt 10): connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections? — retrying in 175s (6465s of 7200s budget left)
psycopg connect failed (attempt 10): connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections? — retrying in 243s (6469s of 7200s budget left)
psycopg connect failed (attempt 10): connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections? — retrying in 162s (6470s of 7200s budget left)
psycopg connect failed (attempt 9): connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections? — retrying in 257s (6457s of 7200s budget left)
psycopg connect failed (attempt 10): connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: '5432', hostaddr: '::1': connection failed: connection to server at "::1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
- host: 'localhost', port: '5432', hostaddr: '127.0.0.1': connection failed: connection to server at "127.0.0.1", port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections? — retrying in 209s (6452s of 7200s budget left)
make[2]: *** [Makefile:1847: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-06-14T04-49-50_20260614T044950-confirm-9a8d0f35f6cc789a_native_kv_vocab_20k_lowfreq_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `9a8d0f35f6cc789a` | `` |
| PR AUC | 0.9988 | 0.0000 |
| ROC AUC | 0.9989 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
