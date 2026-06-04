# Code Analysis

## Core Files

- `src/bss_pipeline/bss_complete_system.py`: integrated demand prediction, order generation, and fleet configuration.
- `src/path_optimization/Intermodal_ALNS_0625.py`: ALNS route optimization program.
- `data/templates/Intermodal_EGS_data_all.xlsx`: template workbook containing `N`, `T`, historical `R*`, `K`, and `o` sheets.
- `data/alns_support/`: ALNS support files for distance, no-route, and fixed-route constraints.

## Demand Prediction

The demand module is implemented by `BSSDemandPredictor`.

Process:

1. `load_and_combine_data(csv_files)` reads CitiBike CSV files in chunks.
2. It filters trips involving 10 selected NYC stations.
3. It extracts `hour`, `day_of_week`, and `day`.
4. `prepare_time_series_split()` uses the first 12 days as training data and the following 3 days as test data.
5. `create_hourly_demand_features()` computes station-hour departure demand, arrival demand, and `net_demand = departure - arrival`.
6. `train_model()` trains an XGBoost regressor if `xgboost` and `scikit-learn` are installed.
7. `predict_demand()` predicts net demand for the test period. If the ML model is unavailable, it falls back to generated simple predictions.

The station list is hard-coded in `BSSDemandPredictor.__init__`.

## Prediction to Orders

`BSSCompleteSystem.convert_predictions_to_orders()` converts predicted positive net demand into ALNS order rows:

- `p`: pickup/source station needing bike movement.
- `d`: randomly selected destination station from the other selected stations.
- `ap`, `bp`: pickup time window.
- `ad`, `bd`: delivery time window.
- `qr`: demand quantity, capped at 40.

Orders with absolute predicted demand below 5 are skipped.

`distribute_orders_to_sheets()` writes order subsets to:

- `R`
- `R_10`
- `R_20`
- `R_50`
- `R_100`

## Fleet Configuration

The fleet module is implemented by `BSSFleetOptimizer`.

Traditional branch:

- Reads candidate vehicle types from the template `K` sheet.
- Computes total order demand and maximum single-order demand.
- Greedily selects vehicles by capacity and a cost-efficiency score.
- Ensures at least 5 vehicles are present.

Neural branch:

- Requires TensorFlow and scikit-learn.
- Builds a small dense neural network.
- Uses the traditional selector to generate labels for training.
- If dependencies or training are unavailable, it falls back to the traditional method.

The output workbook writes the selected vehicles into sheet `K`.

## Connection Between Demand Prediction and ALNS

The integration is currently file-based:

1. Demand prediction creates station-hour net-demand predictions.
2. The system converts these predictions into ALNS order sheets `R*`.
3. Fleet configuration selects vehicles and writes sheet `K`.
4. `create_o_sheet_data()` assigns each vehicle an origin and destination for sheet `o`.
5. `create_single_excel_file()` copies template sheets `N` and `T`, then writes `R*`, `K`, and `o`.
6. ALNS reads the generated Excel file as `Intermodal_EGS_data_all.xlsx`.

So the current integration is complete at the input-data level: prediction-driven orders and vehicle settings are passed to path optimization through the Excel workbook.

## Path Optimization

`Intermodal_ALNS_0625.py` is a large ALNS experiment script. Key behavior:

- The default entry point is `real_main(3)`.
- It sets `data_path = "Intermodal_EGS_data_all.xlsx"`.
- It reads `R_50` by default because `request_number_in_R = 50`.
- It reads `K`, `o`, `N`, `T`, distance workbook `D_EGS - 10r.xlsx`, no-route workbook `Barge_no_land.xlsx`, and fixed-route workbook `Fixed_right_real.xlsx`.
- It constructs routes, checks capacity and time constraints, applies insertion/removal operators, simulated annealing acceptance, and records best routes/objectives.
- Output is written under `Figures/experiment.../` and `results/`.

## Current Limitations

- The integrated pipeline uses a hard-coded list of 10 NYC stations.
- Destination station assignment in generated orders is random.
- The template `N/T` sheets may come from a previous scenario; verify station names before serious ALNS experiments.
- ALNS still uses fixed filenames and internal parameter edits rather than a clean CLI.
- Full CitiBike raw CSV files are not in the repository because of GitHub size limits.
