# Azoth Filetype Night Tranche

Created: 2026-05-07

Script:

```sh
scripts/run_azoth_filetype_night_tranche.sh
```

Purpose: run eight hand-selected probes for every named filetype with at least
50 malware and 50 benign examples. Routes are ordered from smallest eligible
pool to largest so an interrupted overnight run still covers sparse specialists
first.

Profile:

- Serial execution.
- Default probe: 80k train / 22k external / 120 trees / 64 workers.
- PE, JavaScript, C, Python, and XML cap at 90k train / 25k external /
  130 trees.
- Score filter disabled for all filetype routes.
- Exact duplicate runs are skipped by `make experiment` unless `EXP_RERUN=1`.
- Many probes use experimental `symbols`, `kv`, and `textenc`; winners need
  litmus feature parity before deployment.
- The empty-string pseudo-filetype is excluded; it is not deployable.

Resume controls:

```sh
RUN_LIMIT=24 scripts/run_azoth_filetype_night_tranche.sh
RUN_SKIP=24 RUN_LIMIT=24 scripts/run_azoth_filetype_night_tranche.sh
scripts/run_azoth_filetype_night_tranche.sh --list
```

Confirmation linkage:

- Use [AZOTH-CONFIRMATION.md](AZOTH-CONFIRMATION.md) for promotion discipline.
- Treat this tranche as screening. Confirm clear wins with routed full-corpus
  policy metrics before changing defaults.

Outcome log:

- 2026-05-07: initial eight-filetype tranche was stopped because it was too
  narrow for the requested scope.
- 2026-05-07: replaced with manifest-driven all-filetype tranche: 51 named
  filetypes, 8 experiments each, 408 total screens. Not yet summarized.
