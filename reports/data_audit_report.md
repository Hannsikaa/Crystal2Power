# Crystal2Power — Dataset Audit Report

- **Dataset File**: `Solar Cell data set.csv`
- **Total Rows**: 42,443
- **Total Columns**: 30
- **Duplicate Rows**: 1,358

## Target Column (`JV_default_PCE`) Analysis
- **Present**: Yes
- **Valid PCE Records**: 41,519 (97.82%)
- **Missing Target Records**: 924
- **Observed Range**: [0.0, 36.2] %
- **Mean**: 12.032 %
- **Median**: 12.73 %
- **Std Dev**: 5.229 %

### Quality Warnings
- ⚠️ Detected 1358 duplicate rows (3.2%). These may represent repeated fabrication experiments or duplicate literature records.
- ⚠️ 3 columns have >60% missing values (e.g., Perovskite_additives_compounds, Perovskite_additives_concentrations, Perovskite_thickness). Imputation indicators or robust handling will be applied.
- ⚠️ Found 72 zero-efficiency (PCE = 0%) entries. These typically represent shunted or failed fabrication runs.

## Columns Profile
| Column Name | Data Type | Missing Count | Missing % | Unique Count | Sample |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Cell_stack_sequence` | `str` | 0 | 0.0% | 5531 | SLG | FTO | TiO2-c | TiO2-mp | Perovskite | Spiro- |
| `Cell_architecture` | `str` | 0 | 0.0% | 7 | nip |
| `Substrate_stack_sequence` | `str` | 0 | 0.0% | 194 | SLG | FTO |
| `ETL_stack_sequence` | `str` | 0 | 0.0% | 1444 | TiO2-c | TiO2-mp |
| `ETL_deposition_procedure` | `str` | 0 | 0.0% | 366 | Spray-pyrolys | Spin-coating |
| `Perovskite_composition_a_ions` | `str` | 29 | 0.07% | 264 | Cs |
| `Perovskite_composition_b_ions` | `str` | 5 | 0.01% | 52 | Sn |
| `Perovskite_composition_c_ions` | `str` | 5 | 0.01% | 33 | I |
| `Perovskite_composition_short_form` | `str` | 0 | 0.0% | 443 | CsSnI |
| `Perovskite_additives_compounds` | `str` | 28672 | 67.55% | 979 | SnF2 |
| `Perovskite_additives_concentrations` | `str` | 37547 | 88.46% | 706 | 0.2 |
| `Perovskite_thickness` | `str` | 29126 | 68.62% | 368 | 400.0 |
| `Perovskite_deposition_number_of_deposition_steps` | `int64` | 0 | 0.0% | 10 | 1 |
| `Perovskite_deposition_procedure` | `str` | 0 | 0.0% | 198 | Spin-coating |
| `Perovskite_deposition_solvents` | `str` | 0 | 0.0% | 342 | DMSO |
| `Perovskite_deposition_quenching_induced_crystallisation` | `bool` | 0 | 0.0% | 2 | False |
| `Perovskite_deposition_thermal_annealing_temperature` | `str` | 0 | 0.0% | 870 | 100 |
| `Perovskite_deposition_thermal_annealing_time` | `str` | 0 | 0.0% | 766 | 10.0 |
| `HTL_stack_sequence` | `str` | 0 | 0.0% | 1959 | Spiro-MeOTAD |
| `HTL_deposition_procedure` | `str` | 0 | 0.0% | 120 | Spin-coating |
| `Backcontact_stack_sequence` | `str` | 0 | 0.0% | 288 | Au |
| `Backcontact_thickness_list` | `str` | 7974 | 18.79% | 383 | 90.0 |
| `Backcontact_deposition_procedure` | `str` | 0 | 0.0% | 113 | Evaporation |
| `Encapsulation` | `bool` | 0 | 0.0% | 2 | False |
| `Encapsulation_stack_sequence` | `str` | 0 | 0.0% | 118 | Unknown |
| `JV_measured` | `bool` | 0 | 0.0% | 2 | True |
| `JV_default_Voc` | `float64` | 2134 | 5.03% | 1183 | 0.002 |
| `JV_default_Jsc` | `float64` | 2099 | 4.95% | 3583 | 0.22 |
| `JV_default_FF` | `float64` | 2286 | 5.39% | 742 | 0.57 |
| `JV_default_PCE` | `float64` | 924 | 2.18% | 2313 | 0.0 |