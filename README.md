# Bike Sharing Rebalancing Program

This repository is about the bike-sharing rebalancing project. 

## Repository Layout

- `src/bss_pipeline/`: integrated demand prediction and fleet configuration code.
- `src/path_optimization/`: ALNS path optimization code and helper scripts.
- `data/templates/`: Excel templates used by the integrated pipeline and ALNS.
- `data/alns_support/`: distance, no-route, and fixed-route workbooks required by ALNS.
- `data/raw/citibike_sample/`: small CitiBike CSV sample that can run the pipeline quickly.
- `docs/`: running guide, code analysis, literature, figures, and project materials.
- `outputs/`: historical result files kept for comparison.

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r src\bss_pipeline\requirements.txt
python src\bss_pipeline\bss_complete_system.py 10 --result-dir outputs\generated_bss_inputs
```

For a complete reproduction guide, read `docs/RUNNING.md`.

## Current Integration Status

The integrated pipeline does the following:

1. Reads CitiBike CSV trip data.
2. Builds station-hour demand features for 10 selected NYC stations.
3. Predicts net demand with XGBoost when dependencies are installed, or falls back to simple generated demand.
4. Converts positive predicted demand into order sheets `R`, `R_10`, `R_20`, `R_50`, and `R_100`.
5. Selects vehicles with a traditional heuristic and, when TensorFlow is available, a neural-network-assisted variant.
6. Writes ALNS-compatible Excel files containing `N`, `T`, `R*`, `K`, and `o` sheets.

See `docs/CODE_ANALYSIS.md` for a more detailed explanation.
