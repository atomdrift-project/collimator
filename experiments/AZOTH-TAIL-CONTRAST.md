# Azoth Tail-Contrast Sweep

- Timestamp: `2026-05-04T03:48:20.878589+00:00`
- Score snapshot: `199337321`
- Eligible filetypes: 40
- Completed: 40

| Filetype | Train bad/good | Cal bad/good | Best rule | L5 hostile recall @ FP | Local best | Local F1 | Local accuracy |
|---|---:|---:|---|---:|---:|---:|---:|
| `pe` | 289158/117359 | 290279/133030 | replacement | 70.19% @ 9 | specialist_primary 74.09% @ 1 | 85.12% | 82.23% |
| `javascript` | 49431/291198 | 56552/333111 | or | 55.06% @ 9 | elf_only 96.48% @ 1 | 98.21% | 99.49% |
| `elf` | 18814/94235 | 15610/95323 | or | 48.65% @ 9 | elf_only 99.57% @ 1 | 99.78% | 99.94% |
| `tar.gz` | 17800/8784 | 15692/9256 | replacement | 48.64% @ 9 | or_general_primary 96.05% @ 1 | 97.98% | 97.51% |
| `package.json` | 13511/5630 | 15355/6451 | or | 48.12% @ 9 | elf_only 99.90% @ 1 | 99.95% | 99.93% |
| `zip` | 28720/2563 | 31411/2835 | or | 48.10% @ 9 | specialist_primary 76.92% @ 1 | 86.95% | 78.83% |
| `python` | 10202/85621 | 11667/97779 | or | 47.75% @ 9 | or_general_primary 91.32% @ 1 | 95.46% | 99.07% |
| `pkg-info` | 3232/620 | 3671/702 | or | 47.72% @ 9 | elf_only 100.00% @ 0 | 100.00% | 100.00% |
| `c` | 6528/363541 | 6556/415684 | or | 47.54% @ 9 | specialist_primary 40.79% @ 2 | 57.93% | 99.08% |
| `zst` | 1980/14105 | 2282/16133 | or | 47.43% @ 9 | or_general_primary 98.20% @ 0 | 99.09% | 99.78% |
| `shell` | 1710/31153 | 1756/35576 | or | 47.36% @ 9 | specialist_primary 82.40% @ 1 | 90.32% | 99.17% |
| `macho` | 1164/4231 | 1296/4854 | or | 47.29% @ 9 | or_general_primary 99.15% @ 1 | 99.54% | 99.80% |
| `php` | 1117/14354 | 1247/16375 | or | 47.28% @ 9 | elf_only 99.60% @ 1 | 99.76% | 99.97% |
| `tar` | 932/298 | 1041/338 | or | 47.22% @ 9 | elf_only 99.42% @ 1 | 99.66% | 99.49% |
| `go` | 689/72770 | 804/83316 | or | 47.22% @ 9 | elf_only 84.33% @ 1 | 91.44% | 99.85% |
| `kotlin` | 770/25276 | 626/28870 | or | 47.21% @ 9 | elf_only 99.20% @ 0 | 99.60% | 99.98% |
| `jar` | 482/943 | 569/1061 | or | 47.19% @ 9 | specialist_primary 93.85% @ 1 | 96.74% | 97.79% |
| `csharp` | 561/30072 | 647/34487 | or | 47.16% @ 9 | elf_only 95.21% @ 1 | 97.47% | 99.91% |
| `ole` | 365/4660 | 380/5310 | or | 47.15% @ 9 | elf_only 97.89% @ 0 | 98.94% | 99.86% |
| `vbs` | 608/112 | 578/130 | or | 47.14% @ 9 | specialist_primary 77.51% @ 1 | 87.24% | 81.50% |
| `java_class` | 330/6385 | 364/7262 | or | 47.14% @ 9 | elf_only 95.88% @ 1 | 97.76% | 99.79% |
| `data` | 256/7463 | 299/8570 | or | 47.14% @ 9 | elf_only 98.33% @ 0 | 99.16% | 99.94% |
| `batch` | 298/1323 | 308/1483 | or | 47.14% @ 9 | elf_only 98.38% @ 0 | 99.18% | 99.72% |
| `powershell` | 306/760 | 337/872 | or | 47.13% @ 9 | elf_only 89.61% @ 1 | 94.38% | 97.02% |
| `plist` | 433/7766 | 468/8863 | or | 47.13% @ 9 | or_general_primary 64.53% @ 1 | 78.34% | 98.21% |
| `text` | 537/41140 | 595/47029 | or | 47.12% @ 9 | elf_only 52.77% @ 1 | 69.01% | 99.41% |
| `perl` | 133/19177 | 149/21917 | or | 47.11% @ 9 | elf_only 99.33% @ 0 | 99.66% | 100.00% |
| `xml` | 913/72918 | 1036/83355 | or | 47.10% @ 9 | elf_only 10.23% @ 1 | 18.55% | 98.90% |
| `python-bytecode` | 80/7328 | 84/8406 | or | 47.10% @ 9 | elf_only 100.00% @ 0 | 100.00% | 100.00% |
| `ruby` | 62/10485 | 69/11944 | or | 47.09% @ 9 | elf_only 100.00% @ 0 | 100.00% | 100.00% |
| `makefile` | 71/15493 | 65/17762 | or | 47.09% @ 9 | elf_only 95.38% @ 0 | 97.64% | 99.98% |
| `gz` | 189/23912 | 179/27297 | or | 47.09% @ 9 | specialist_primary 29.05% @ 0 | 45.02% | 99.54% |
| `pdf` | 69/1841 | 57/2118 | or | 47.09% @ 9 | elf_only 100.00% @ 1 | 99.13% | 99.95% |
| `rtf` | 78/365 | 69/408 | or | 47.09% @ 9 | or_general_primary 97.10% @ 1 | 97.81% | 99.37% |
| `jpeg` | 616/5725 | 513/6496 | or | 47.08% @ 9 | or_general_primary 3.70% @ 0 | 7.14% | 92.95% |
| `png` | 3863/52577 | 3411/60254 | or | 47.08% @ 9 | or_general_primary 2.52% @ 1 | 4.92% | 94.78% |
| `rust` | 46/55638 | 52/63549 | or | 47.08% @ 9 | general_only 25.00% @ 1 | 39.39% | 99.94% |
| `unknown` | 84/12310 | 88/14095 | or | 47.08% @ 9 | general_only 7.95% @ 1 | 14.58% | 99.42% |
| `docx` | 169/175 | 160/199 | or | 47.08% @ 9 | general_only 78.12% @ 1 | 87.41% | 89.97% |
| `xlsx` | 102/72 | 85/75 | or | 47.08% @ 9 | general_only 55.29% @ 1 | 70.68% | 75.62% |

## Promotion Check: L3 Runtime Policy

Candidate bundle: `out/models/azoth-tail-promote-l3`.

Changes tested against the current deployed ensemble:

- replace `filetypes/pe` with tail-contrast model
- replace `filetypes/tar.gz` with tail-contrast model
- replace `filetypes/package.json` with tail-contrast model
- replace `filetypes/zip` with tail-contrast model

Raw calibration looked better before route-policy search, especially at the new
default L3 hostile point: 59.18% recall at 5 FP versus 53.35% in the current
runtime metric. After route-policy search, however, the actual runtime global
policy metrics were effectively unchanged:

| Bundle | L3 hostile | L3 suspicious | L5 hostile | L9 hostile |
|---|---:|---:|---:|---:|
| current `azoth` | 53.35% @ 5 FP | 64.95% @ 58 FP | 59.80% @ 9 FP | 60.80% @ 16 FP |
| tail candidate | 53.35% @ 5 FP | 64.96% @ 58 FP | 59.81% @ 9 FP | 60.80% @ 16 FP |

Verdict: reject promotion for now. The tail models are useful research
artifacts, but under the current runtime route-policy search they do not raise
the deployed ensemble's effective detection rate. The gap between raw
calibration gains and runtime policy metrics is itself the next thing to fix.
