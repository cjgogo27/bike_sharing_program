# Data Notes

## Included Data

- `data/raw/citibike_sample/202502-citibike-tripdata_3.csv`
  - Small sample copied from the original `BSS/202502-citibike-tripdata/` folder.
  - Contains trips from 2025-02-14 to 2025-02-28.
  - Includes 837 records involving the selected 10 NYC stations after filtering.

- `data/templates/Intermodal_EGS_data_all.xlsx`
  - Main Excel template used by the integrated system.

- `data/alns_support/`
  - `D_EGS - 10r.xlsx`
  - `Barge_no_land.xlsx`
  - `Fixed_right_real.xlsx`

- `data/distance_matrices/`
  - NYC bike and driving distance matrices kept for reference and future improvement.

## Excluded Data

The following full raw files were not committed because they exceed GitHub's normal file size limit:

- `BSS/202502-citibike-tripdata/202502-citibike-tripdata_1.csv` around 186 MB
- `BSS/202502-citibike-tripdata/202502-citibike-tripdata_2.csv` around 186 MB
- large zip archives such as `202502-citibike-tripdata.zip`

Place full raw CSVs in `data/raw/citibike/` when needed. That directory is intentionally git-ignored.
