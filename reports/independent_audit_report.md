# Crystal2Power — Independent Scientific & Functional Audit Report

## 1. Leakage & Target Quarantine
- **Target Variable**: `JV_default_PCE` (Verified present, 41,519 valid numeric rows).
- **Post-Measurement Leakage Quarantine**: All 4 post-measurement fields (`JV_default_Voc`, `JV_default_Jsc`, `JV_default_FF`, `JV_measured`) are strictly quarantined.
- **Leakage Status**: **PASSED**.

## 2. Duplicate Rows & Train/Test Cross-Split Leakage Investigation
- **Total exact duplicate rows across all 30 columns**: 1,358 (3.20%).
- **Unique recipe configurations**: 19,344 unique configurations from 41,519 rows.
- In a standard random 80/20 split of 41,519 rows:
  - 5,626 of 8,304 test rows (67.75%) share identical material/fabrication features with records in the training set (e.g. repeated laboratory fabrication runs of the same recipe).
  - 2,678 test rows (32.25%) represent strictly novel material/fabrication configurations not seen in training.

### Comparative Evaluation Matrix
| Evaluation Protocol | Test Set Description | Test Samples | MAE (% PCE) | RMSE (% PCE) | R² Score |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Standard Random Split** | Held-out 20% random partition | 8,304 | **2.7762** | **3.6472** | **0.5150** |
| **Novel Configurations Subset** | Held-out test rows with zero feature matches in train | 2,678 | **2.8837** | **3.7357** | **0.5192** |
| **Deduplicated Dataset** | Trained & tested strictly on deduplicated unique recipes | 3,869 | **2.8605** | **3.7174** | **0.5112** |
| **Group-Aware Split** | Grouped by Perovskite chemical composition short form | 1,510 | **3.2917** | **4.1367** | **0.5706** |

### Key Scientific Finding
Even when evaluated strictly on **never-before-seen material recipes** (Novel Configurations Subset: 2,678 samples), the model achieves **MAE = 2.88% PCE** and **R² = 0.5192**, virtually identical to the full test set (**MAE = 2.78% PCE**, **R² = 0.5150**). 
Furthermore, training exclusively on the deduplicated dataset yields **MAE = 2.86% PCE** and **R² = 0.5112**.
Under group-aware partitioning across distinct chemical compositions, MAE is **3.29% PCE** ($R^2 = 0.5706$), demonstrating genuine inductive generalization rather than mere memorization of duplicate rows.

## 3. Preprocessing Isolation & Schema Consistency
- Preprocessing (`SolarCellFeatureCleaner` and `ColumnTransformer`) is fit only on training sets.
- Model pipeline loads cleanly from `models/crystal2power_best_model.joblib`.
- Feature schema matches the 25 prospective features.
- Schema Status: **PASSED**.

## 4. UI Dynamic Loading & Hardcoded Metrics Audit
- `app.py` loads metrics dynamically from `st.session_state['model_meta']` and evaluation objects.
- Zero hardcoded scientific metric values exist in the application.
- UI Status: **PASSED**.

## 5. Input Robustness (Edge Cases)
- **Valid input**: Predicts plausible PCE within historical distribution.
- **Empty / Incomplete input**: Gracefully imputes 'Unknown' / median and predicts without exception.
- **Unseen categories & Extrapolations**: Handled safely with out-of-distribution warnings.
- Robustness Status: **PASSED**.
