# Crystal2Power Dataset Directory

Place your experimental solar cell dataset files in this directory.

## Expected Files
- `Solar Cell data set.csv` or any standard CSV / Excel file containing perovskite solar cell fabrication and electrical performance data.
- (Optional) `Solar Cell Dataset.pptx` presentation outlining data descriptions or schemas.

## Primary Target Column
- `JV_default_PCE` (Power Conversion Efficiency in %)

## Input Parameters
Material composition, layer architecture, deposition parameters, thermal annealing conditions, and encapsulation sequence.
Post-measurement parameters (such as `JV_default_Voc`, `JV_default_Jsc`, `JV_default_FF`, `JV_measured`) are strictly excluded during training to prevent target leakage.
