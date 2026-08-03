# Confirm FAIL — 3533e4c65d777e8a on `filegroups/native`

Cycle `20260723T123838-confirm-3533e4c65d777e8a` — 2026-07-23T12:38:38Z

experiment failed: interrupted: context canceled
--- experiment log tail ---
...(truncated)...
INFO  collimator.features: vocab prune @1000 batches: dropped 1454205 singleton n-gram keys (4716544 -> 3262339 entries; bi=698693 tri=2395084 el=11039 tbi=157523 ttri=0)
08:41:50 INFO  collimator.features: vocab prune @1200 batches: dropped 887111 singleton n-gram keys (4456434 -> 3569323 entries; bi=730038 tri=2664987 el=12331 tbi=161967 ttri=0)
08:42:00 INFO  collimator.features: vocab prune @1400 batches: dropped 1032023 singleton n-gram keys (5000980 -> 3968957 entries; bi=774240 tri=3012697 el=13374 tbi=168646 ttri=0)
08:42:22 INFO  collimator.features: vocab prune @1600 batches: dropped 926550 singleton n-gram keys (5351391 -> 4424841 entries; bi=824178 tri=3409328 el=16140 tbi=175195 ttri=0)
08:42:44 INFO  collimator.features: vocab prune @1800 batches: dropped 1004406 singleton n-gram keys (5608596 -> 4604190 entries; bi=839492 tri=3570127 el=18025 tbi=176546 ttri=0)
08:43:06 INFO  collimator.features: vocab prune @2000 batches: dropped 896420 singleton n-gram keys (5657363 -> 4760943 entries; bi=850556 tri=3713180 el=19473 tbi=177734 ttri=0)
08:43:29 INFO  collimator.features: vocab prune @2200 batches: dropped 746721 singleton n-gram keys (5624224 -> 4877503 entries; bi=865784 tri=3812308 el=20518 tbi=178893 ttri=0)
08:43:54 INFO  collimator.features: vocab prune @2400 batches: dropped 1238652 singleton n-gram keys (6621821 -> 5383169 entries; bi=942885 tri=4221510 el=22862 tbi=195912 ttri=0)
08:44:08 INFO  collimator.features: vocab prune @2600 batches: dropped 271246 singleton n-gram keys (5817709 -> 5546463 entries; bi=947452 tri=4378525 el=23170 tbi=197316 ttri=0)
08:45:35 INFO  collimator.features: vocab prune @2800 batches: dropped 1248818 singleton n-gram keys (7319545 -> 6070727 entries; bi=1022539 tri=4811370 el=25233 tbi=211585 ttri=0)
08:46:04 INFO  collimator.features: vocab prune @3000 batches: dropped 1032143 singleton n-gram keys (7580754 -> 6548611 entries; bi=1059249 tri=5234930 el=28682 tbi=225750 ttri=0)
08:46:31 INFO  collimator.features: vocab prune @3200 batches: dropped 951032 singleton n-gram keys (7781543 -> 6830511 entries; bi=1079612 tri=5487410 el=30256 tbi=233233 ttri=0)
08:46:53 INFO  collimator.features: vocab prune @3400 batches: dropped 1097826 singleton n-gram keys (8349189 -> 7251363 entries; bi=1113874 tri=5869810 el=30984 tbi=236695 ttri=0)
08:47:15 INFO  collimator.features: vocab prune @3600 batches: dropped 526549 singleton n-gram keys (7945910 -> 7419361 entries; bi=1147780 tri=5999674 el=32127 tbi=239780 ttri=0)
08:47:36 INFO  collimator.features: vocab prune @3800 batches: dropped 520967 singleton n-gram keys (8027730 -> 7506763 entries; bi=1162800 tri=6068874 el=32747 tbi=242342 ttri=0)
08:48:00 INFO  collimator.features: vocab prune @4000 batches: dropped 421909 singleton n-gram keys (7990913 -> 7569004 entries; bi=1170634 tri=6121917 el=33217 tbi=243236 ttri=0)
08:48:21 INFO  collimator.features: vocab prune @4200 batches: dropped 411633 singleton n-gram keys (8044548 -> 7632915 entries; bi=1178867 tri=6176638 el=33561 tbi=243849 ttri=0)
08:48:43 INFO  collimator.features: vocab prune @4400 batches: dropped 391728 singleton n-gram keys (8073436 -> 7681708 entries; bi=1184859 tri=6218363 el=33875 tbi=244611 ttri=0)
08:49:05 INFO  collimator.features: vocab prune @4600 batches: dropped 544637 singleton n-gram keys (8302507 -> 7757870 entries; bi=1207405 tri=6267373 el=34470 tbi=248622 ttri=0)
08:49:37 INFO  collimator.features: vocab prune @4800 batches: dropped 874180 singleton n-gram keys (9002347 -> 8128167 entries; bi=1260844 tri=6574751 el=36741 tbi=255831 ttri=0)
08:50:04 INFO  collimator.features: vocab prune @5000 batches: dropped 866011 singleton n-gram keys (9186669 -> 8320658 entries; bi=1281153 tri=6743771 el=37714 tbi=258020 ttri=0)
08:50:29 INFO  collimator.features: vocab prune @5200 batches: dropped 810427 singleton n-gram keys (9239541 -> 8429114 entries; bi=1295062 tri=6835457 el=38430 tbi=260165 ttri=0)
make[1]: *** [Makefile:1913: experiment] Terminated
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-07-23T12-38-38_20260723T123838-confirm-3533e4c65d777e8a_inherit_from_filetypes_plist_8b54303f_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `3533e4c65d777e8a` | `` |
| PR AUC | 0.9991 | 0.0000 |
| ROC AUC | 0.9992 | 0.0000 |
| Recall@3FPM | — | 0.0000 |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
