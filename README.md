# Crystal2Power AI — Optimization of Perovskite Solar Cell Performance

![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-red.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5%2B-orange.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-teal.svg)
![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen.svg)

**Crystal2Power AI** is an academic machine learning web application developed for photovoltaic researchers, materials scientists, and students. It predicts the **Power Conversion Efficiency (PCE %)** of perovskite solar cells directly from material compositions, device layer sequences, and thermal annealing parameters.

The platform is designed to assist prospective materials screening and prevent the common pitfall of **target leakage** in solar cell literature.

---

## 🌟 Key Features

1. **Automated Scientific Data Audit**:
   - Ingests experimental perovskite datasets (.csv, .xlsx, .parquet).
   - Profiles 30+ physical fields: missingness, unique categories, duplicate device counts, and anomaly indicators.
   - Detects inactive shunted cells (PCE = 0%) and suspicious records (>40% PCE).
   - Generates downloadable Markdown audit reports.

2. **Rigorous Target Leakage Prevention**:
   - Enforces strict quarantine on post-measurement electrical variables (`JV_default_Voc`, `JV_default_Jsc`, `JV_default_FF`, `JV_measured`).
   - Ensures models predict PCE *before* device characterization, enabling true prospective screening.

3. **Multi-Algorithm Regression Benchmark**:
   - Compares:
     - `DummyRegressor` (mean baseline)
     - `HistGradientBoostingRegressor`
     - `RandomForestRegressor`
     - `ExtraTreesRegressor`
   - K-fold cross-validation on training data to select the optimal model.
   - Honest held-out test set evaluation (MAE, RMSE, R²).

4. **Model Explainability & Feature Importance**:
   - Permutation importance on the full held-out test pipeline.
   - Highlights top influential physical parameters (absorber thickness, cation mix, annealing temperature, transport layers).
   - Distinguishes learned statistical correlation from experimental physical causation.

5. **Interactive Prediction Calculator & Champion Recipe Comparison**:
   - Dynamic parameter inputs with unit validation (nm, °C, min).
   - Out-of-distribution range checks and unseen-category safety handling.
   - Compares canonical perovskite formulations (Standard $MAPbI_3$, Triple-Cation $CsFAMA$, Lead-Free $CsSnI_3$).

---

## 🏗️ Project Architecture

```
crystal2power/
│
├── app.py                     # Interactive Streamlit Web Application
├── train_real_model.py        # CLI training script on real dataset
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive documentation and guide
├── .gitignore                 # Version control exclusions
│
├── .streamlit/
│   └── config.toml            # Scientific UI theme styling & server configuration
│
├── data/
│   ├── README.md              # Instructions for dataset placement
│   ├── Solar Cell data set.csv # Real tabular dataset (42,443 records)
│   └── Solar Cell Dataset.pptx# Schema & domain presentation
│
├── models/
│   ├── crystal2power_best_model.joblib        # Persisted best model pipeline
│   └── crystal2power_best_model_metadata.json # Training metadata & test metrics
│
├── reports/
│   └── data_audit_report.md   # Generated data audit report
│
├── src/
│   ├── __init__.py            # Package init
│   ├── data_loader.py         # Multi-encoding CSV/Excel loading & target check
│   ├── data_audit.py          # Data profiling, summary stats & anomaly detection
│   ├── leakage.py             # Leakage audit & post-measurement quarantine
│   ├── preprocessing.py       # Regex cleaners, ColumnTransformer & Pipelines
│   ├── train.py               # Model training, CV benchmark & joblib persistence
│   ├── evaluate.py            # Regression metrics (MAE, RMSE, R²) & residuals
│   ├── predict.py             # Single and batch prediction with plausibility checks
│   └── explain.py             # Permutation feature importance on held-out data
│
└── tests/
    ├── test_data_loader.py    # CSV/Excel loading and validation tests
    ├── test_preprocessing.py  # Number extractors and unseen category tests
    ├── test_leakage.py        # Leakage exclusion assertions
    └── test_model_pipeline.py # End-to-end training & prediction tests
```

---

## ⚡ Setup & Installation Instructions (Windows)

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13 installed.
- PowerShell or Windows Terminal.

### 2. Create Virtual Environment
Open PowerShell inside the `crystal2power` project directory:

```powershell
py -m venv .venv
```

Activate the virtual environment:
```powershell
.venv\Scripts\Activate.ps1
```

*(If script execution is disabled on your system, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

### 3. Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🚀 Running the Project

### 1. Launch the Web Application
```powershell
python -m streamlit run app.py
```
Streamlit will automatically launch in your default web browser at:
`http://localhost:8501`

### 2. Run Automated Test Suite
Run the full pytest suite to verify all unit and integration tests:
```powershell
python -m pytest -v
```

### 3. Retrain Model via Command Line (Optional)
To retrain the benchmark models and regenerate the data audit report from the terminal:
```powershell
python -u train_real_model.py
```

---

## 🛡️ Target Leakage Prevention: Scientific Rationale

Power Conversion Efficiency is calculated from illuminated current-voltage ($J$-$V$) curves using:

$$\text{PCE} = \frac{V_{oc} \cdot J_{sc} \cdot FF}{P_{in}} \times 100\%$$

In machine learning workflows, including $V_{oc}$, $J_{sc}$, or $FF$ as input features results in ~99% artificial $R^2$. However, this is **target leakage**: these three parameters can only be measured **after the solar cell has already been manufactured and tested in a solar simulator**.

Crystal2Power enforces the following quarantine:

| Column | Status | Reason |
| :--- | :--- | :--- |
| `JV_default_PCE` | **EXCLUDED** | Prediction target. |
| `JV_default_Voc` | **EXCLUDED** | Post-measurement open-circuit voltage. |
| `JV_default_Jsc` | **EXCLUDED** | Post-measurement short-circuit current density. |
| `JV_default_FF` | **EXCLUDED** | Post-measurement fill factor. |
| `JV_measured` | **EXCLUDED** | Measurement status indicator. |
| All Architecture, Material, and Deposition Columns | **INCLUDED** | Known *prior* to device fabrication. |

---

## 📊 Model Evaluation & Metric Interpretations

- **MAE (Mean Absolute Error)**: Average absolute difference between predicted and actual PCE in percentage points (% PCE).
- **RMSE (Root Mean Squared Error)**: Penalizes larger prediction outliers more heavily.
- **$R^2$ (Coefficient of Determination)**: Proportion of variance explained by prospective features relative to predicting the overall mean.
- **Negative $R^2$**: If a model yields negative $R^2$, it performs worse than simply predicting the training mean, indicating severe underfitting or out-of-distribution test samples.

### 🔬 Duplicate Row & Cross-Split Generalization Audit

The dataset contains 1,358 exact duplicate rows (3.2%) and multiple repeated laboratory runs of identical nominal formulations. To verify whether random-split performance was artificially inflated by memorization, an independent partition audit was conducted:

| Split / Evaluation Protocol | Test Set Description | Samples | MAE (% PCE) | RMSE (% PCE) | $R^2$ |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Standard Random Split** | Held-out 20% random partition | 8,304 | **2.78** | **3.65** | **0.515** |
| **Novel Formulations Subset** | Test samples with zero matching recipes in training | 2,678 | **2.88** | **3.74** | **0.519** |
| **Deduplicated Dataset** | Trained & tested on unique recipes only | 3,869 | **2.86** | **3.72** | **0.511** |
| **Group-Aware Split** | Grouped by perovskite chemical formula | 1,510 | **3.29** | **4.14** | **0.571** |

**Conclusion**: The model maintains consistent error (~2.88% MAE) on completely novel, unseen formulations, verifying genuine inductive learning rather than duplicate memorization.

---

## ⚠️ Scientific Limitations

1. **Correlated Material Formulations**: Additives (e.g., $SnF_2$ in tin perovskites) and charge transport layers are often chosen in conjunction. Feature importance reflects empirical association in literature, not proven laboratory causation.
2. **Missing Nanoscale Morphology**: Grain boundary defects, pinholes, and interfacial traps are critical determinants of recombination but are not directly captured in tabular datasets.
3. **Inter-Laboratory Variance**: Ambient glovebox humidity, precursor purity, and spin-coating dynamics introduce unavoidable variance across different research groups.
"# Crystal2Power" 
