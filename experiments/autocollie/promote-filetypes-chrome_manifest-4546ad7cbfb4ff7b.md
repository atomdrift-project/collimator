# Promote REJECTED — `4546ad7cbfb4ff7b` on `filetypes/chrome_manifest`

Generated 2026-10-31T00:04:33Z

azoth-validate failed: exit status 2 (log /home/t/src/collimator/out/autocollie/runs/2026-10-30T23-20-05_20261030T231959-promote-4546ad7cbfb4ff7b_azoth-validate.log; tail:     main()
    ~~~~^^
  File "/home/t/src/collimator/src/collimator/__main__.py", line 833, in main
    thresholds.tune_thresholds(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~^
        db_path=_db_dsn(args.db),
        ^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<12 lines>...
        refresh_cache=args.refresh_cache,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/t/src/collimator/src/collimator/thresholds/_inspect.py", line 395, in tune_thresholds
    samples, probs, y = _score_labeled_corpus(
                        ~~~~~~~~~~~~~~~~~~~~~^
        db_path,
        ^^^^^^^^
    ...<10 lines>...
        include_samples=top_errors > 0 and not scores_only,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/t/src/collimator/src/collimator/thresholds/_inspect.py", line 319, in _score_labeled_corpus
    np.savez(
    ~~~~~~~~^
        tmp_path,
        ^^^^^^^^^
    ...<20 lines>...
        corpus_requested_max_id=np.array(int(max_id), dtype=np.int64),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/t/src/collimator/.venv/lib/python3.14/site-packages/numpy/lib/_npyio_impl.py", line 673, in savez
    _savez(file, args, kwds, False, allow_pickle=allow_pickle)
    ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/.venv/lib/python3.14/site-packages/numpy/lib/_npyio_impl.py", line 786, in _savez
    format.write_array(fid, val,
    ~~~~~~~~~~~~~~~~~~^^^^^^^^^^
                       allow_pickle=allow_pickle,
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^
                       pickle_kwargs=pickle_kwargs)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/.venv/lib/python3.14/site-packages/numpy/lib/_format_impl.py", line 777, in write_array
    fp.write(chunk.tobytes('C'))
    ~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/zipfile/__init__.py", line 1367, in write
    self._fileobj.write(data)
    ~~~~~~~~~~~~~~~~~~~^^^^^^
OSError: [Errno 28] No space left on device
make: *** [Makefile:1251: azoth-calibrate] Error 1)

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9390 -> 0.9390; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `4546ad7cbfb4ff7b` | `a0b4d0f7bc0dfc66` | `388e330abf97f28a` |
| PR AUC | 0.9390 | 0.9390 | 0.9556 |
| ROC AUC | 0.9933 | 0.9933 | 0.9950 |
| F1 | 0.6429 | 0.8889 | 0.9412 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/src/collimator/out/autocollie/runs/2026-10-30T23-20-05_20261030T231959-promote-4546ad7cbfb4ff7b_azoth-validate.log; tail:     main()
    ~~~~^^
  File "/home/t/src/collimator/src/collimator/__main__.py", line 833, in main
    thresholds.tune_thresholds(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~^
        db_path=_db_dsn(args.db),
        ^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<12 lines>...
        refresh_cache=args.refresh_cache,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/t/src/collimator/src/collimator/thresholds/_inspect.py", line 395, in tune_thresholds
    samples, probs, y = _score_labeled_corpus(
                        ~~~~~~~~~~~~~~~~~~~~~^
        db_path,
        ^^^^^^^^
    ...<10 lines>...
        include_samples=top_errors > 0 and not scores_only,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/t/src/collimator/src/collimator/thresholds/_inspect.py", line 319, in _score_labeled_corpus
    np.savez(
    ~~~~~~~~^
        tmp_path,
        ^^^^^^^^^
    ...<20 lines>...
        corpus_requested_max_id=np.array(int(max_id), dtype=np.int64),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/t/src/collimator/.venv/lib/python3.14/site-packages/numpy/lib/_npyio_impl.py", line 673, in savez
    _savez(file, args, kwds, False, allow_pickle=allow_pickle)
    ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/.venv/lib/python3.14/site-packages/numpy/lib/_npyio_impl.py", line 786, in _savez
    format.write_array(fid, val,
    ~~~~~~~~~~~~~~~~~~^^^^^^^^^^
                       allow_pickle=allow_pickle,
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^
                       pickle_kwargs=pickle_kwargs)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/.venv/lib/python3.14/site-packages/numpy/lib/_format_impl.py", line 777, in write_array
    fp.write(chunk.tobytes('C'))
    ~~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.14/zipfile/__init__.py", line 1367, in write
    self._fileobj.write(data)
    ~~~~~~~~~~~~~~~~~~~^^^^^^
OSError: [Errno 28] No space left on device
make: *** [Makefile:1251: azoth-calibrate] Error 1)
