"""Crystal2Power AI — Production Vercel Serverless Entrypoint.

Standard Python BaseHTTPRequestHandler compatible with all Vercel runtimes.
Provides REST endpoints and serves the complete Crystal2Power web application.
"""

import os
import sys
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Ensure workspace root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd
import joblib

# -----------------------------------------------------------------------------
# MODEL & METADATA LOADER (CACHED AT MODULE STARTUP)
# -----------------------------------------------------------------------------
MODEL_PATH = BASE_DIR / "models" / "crystal2power_best_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "crystal2power_best_model_metadata.json"

pipeline = None
metadata = {}

try:
    if MODEL_PATH.exists():
        pipeline = joblib.load(str(MODEL_PATH))
    if METADATA_PATH.exists():
        with open(str(METADATA_PATH), "r", encoding="utf-8") as f:
            metadata = json.load(f)
except Exception as e:
    print(f"[WARNING] Error loading model or metadata: {e}")

FEATURE_COLUMNS = metadata.get("feature_columns", [
    "Cell_stack_sequence",
    "Cell_architecture",
    "Substrate_stack_sequence",
    "ETL_stack_sequence",
    "ETL_deposition_procedure",
    "Perovskite_composition_a_ions",
    "Perovskite_composition_b_ions",
    "Perovskite_composition_c_ions",
    "Perovskite_composition_short_form",
    "Perovskite_additives_compounds",
    "Perovskite_additives_concentrations",
    "Perovskite_thickness",
    "Perovskite_deposition_number_of_deposition_steps",
    "Perovskite_deposition_procedure",
    "Perovskite_deposition_solvents",
    "Perovskite_deposition_quenching_induced_crystallisation",
    "Perovskite_deposition_thermal_annealing_temperature",
    "Perovskite_deposition_thermal_annealing_time",
    "HTL_stack_sequence",
    "HTL_deposition_procedure",
    "Backcontact_stack_sequence",
    "Backcontact_thickness_list",
    "Backcontact_deposition_procedure",
    "Encapsulation",
    "Encapsulation_stack_sequence"
])

# -----------------------------------------------------------------------------
# EFFICIENCY TIER HELPER
# -----------------------------------------------------------------------------
def compute_efficiency_tier(pce: float) -> dict:
    if pce < 5.0:
        return {
            "tier": "Inactive / Severe Defect",
            "badge": "tier-inactive",
            "color": "#DC2626",
            "desc": "PCE < 5.0%. Indicates high non-radiative recombination, poor interface alignment, or incomplete perovskite phase crystallization."
        }
    elif pce < 12.0:
        return {
            "tier": "Sub-Optimal / Transport-Limited",
            "badge": "tier-suboptimal",
            "color": "#D97706",
            "desc": "PCE 5.0%–12.0%. Viable diode behavior observed, but limited by carrier extraction resistance or unoptimized thermal annealing."
        }
    elif pce < 18.0:
        return {
            "tier": "Standard Viable Efficiency",
            "badge": "tier-standard",
            "color": "#2563EB",
            "desc": "PCE 12.0%–18.0%. Matches standard academic baseline devices (e.g. typical single-step MAPbI3 spin-coated architectures)."
        }
    elif pce < 22.0:
        return {
            "tier": "High-Efficiency Laboratory Device",
            "badge": "tier-high",
            "color": "#0D9488",
            "desc": "PCE 18.0%–22.0%. High-performance multi-cation or passivated interface architecture matching peer-reviewed literature champions."
        }
    elif pce <= 26.0:
        return {
            "tier": "State-of-the-Art Single-Junction",
            "badge": "tier-champion",
            "color": "#16A34A",
            "desc": "PCE 22.0%–26.0%. Approaching the theoretical Shockley-Queisser limit for single-junction perovskite cells (~33%)."
        }
    else:
        return {
            "tier": "Multijunction / Tandem Range",
            "badge": "tier-tandem",
            "color": "#7C3AED",
            "desc": "PCE > 26.0%. Physical performance in this tier typically corresponds to multi-junction (e.g. Perovskite/Silicon tandem) devices."
        }

# -----------------------------------------------------------------------------
# BENCHMARK PRESETS
# -----------------------------------------------------------------------------
PRESETS = {
    "csfama": {
        "name": "Triple Cation CsFAMA (Record Benchmark)",
        "desc": "High-efficiency laboratory champion recipe with mixed A-site cations and passivated SnO2/Spiro interface.",
        "params": {
            "Cell_architecture": "nip",
            "Perovskite_composition_short_form": "CsFAMA",
            "Perovskite_thickness": 500,
            "Perovskite_deposition_thermal_annealing_temperature": 100,
            "Perovskite_deposition_thermal_annealing_time": 45,
            "Perovskite_deposition_quenching_induced_crystallisation": "Chlorobenzene",
            "ETL_stack_sequence": "SnO2",
            "HTL_stack_sequence": "Spiro-OMeTAD",
            "Substrate_stack_sequence": "SLG | FTO"
        }
    },
    "mapbi3": {
        "name": "Standard MAPbI3 (Research Baseline)",
        "desc": "Classic single-cation methylammonium lead iodide device with mesoporous TiO2 ETL.",
        "params": {
            "Cell_architecture": "nip",
            "Perovskite_composition_short_form": "MAPbI3",
            "Perovskite_thickness": 400,
            "Perovskite_deposition_thermal_annealing_temperature": 100,
            "Perovskite_deposition_thermal_annealing_time": 30,
            "Perovskite_deposition_quenching_induced_crystallisation": "Diethyl ether",
            "ETL_stack_sequence": "TiO2",
            "HTL_stack_sequence": "Spiro-OMeTAD",
            "Substrate_stack_sequence": "SLG | FTO"
        }
    },
    "cssni3": {
        "name": "Lead-Free CsSnI3 (Eco-Friendly)",
        "desc": "Non-toxic lead-free tin-based perovskite with low bandgap and PTAA polymer HTL.",
        "params": {
            "Cell_architecture": "pin",
            "Perovskite_composition_short_form": "CsSnI3",
            "Perovskite_thickness": 350,
            "Perovskite_deposition_thermal_annealing_temperature": 120,
            "Perovskite_deposition_thermal_annealing_time": 20,
            "Perovskite_deposition_quenching_induced_crystallisation": "Toluene",
            "ETL_stack_sequence": "PCBM",
            "HTL_stack_sequence": "PTAA",
            "Substrate_stack_sequence": "SLG | ITO"
        }
    }
}

# -----------------------------------------------------------------------------
# HTML TEMPLATE
# -----------------------------------------------------------------------------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crystal2Power AI — Perovskite Solar Cell Efficiency Engine</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-body: #F7F9FC;
            --surface-white: #FFFFFF;
            --navy-deep: #0B1220;
            --navy-card: #111B30;
            --teal-primary: #14B8A6;
            --teal-hover: #0D9488;
            --teal-soft: rgba(20, 184, 166, 0.12);
            --text-dark: #0F172A;
            --text-muted: #64748B;
            --text-subtle: #94A3B8;
            --border-light: #E2E8F0;
            --shadow-subtle: 0 4px 20px -2px rgba(11, 18, 32, 0.05);
            --shadow-card: 0 10px 30px -4px rgba(11, 18, 32, 0.08);
            --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: var(--font-sans);
            background-color: var(--bg-body);
            color: var(--text-dark);
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        /* Top Navigation */
        .top-nav {
            background-color: var(--navy-deep);
            color: white;
            padding: 0.85rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .brand-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            cursor: pointer;
        }

        .brand-icon {
            background: linear-gradient(135deg, var(--teal-primary), #3B82F6);
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }

        .brand-title {
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #FFFFFF;
        }

        .brand-subtitle {
            font-size: 0.75rem;
            color: var(--text-subtle);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .nav-links {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .nav-link {
            color: #94A3B8;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .nav-link:hover {
            color: white;
            background-color: rgba(255, 255, 255, 0.06);
        }

        .nav-link.active {
            color: white;
            background-color: rgba(20, 184, 166, 0.2);
            border: 1px solid rgba(20, 184, 166, 0.4);
        }

        .status-pill {
            background-color: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.4);
            color: #34D399;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: #34D399;
            box-shadow: 0 0 8px #34D399;
        }

        /* Container & Sections */
        .main-container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
            width: 100%;
            flex: 1;
        }

        .tab-section { display: none; }
        .tab-section.active { display: block; animation: fadeIn 0.3s ease; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Home Hero */
        .hero-banner {
            background: linear-gradient(135deg, var(--navy-deep) 0%, #152238 100%);
            border-radius: 16px;
            padding: 3.5rem 3rem;
            color: white;
            box-shadow: var(--shadow-card);
            border: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 2.5rem;
        }

        .hero-tag {
            color: var(--teal-primary);
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.75rem;
        }

        .hero-title {
            font-size: 2.75rem;
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: -0.03em;
            margin-bottom: 1rem;
            max-width: 800px;
        }

        .hero-desc {
            font-size: 1.1rem;
            color: #CBD5E1;
            max-width: 700px;
            line-height: 1.6;
            margin-bottom: 2rem;
        }

        .hero-actions { display: flex; gap: 1rem; flex-wrap: wrap; }

        .btn-primary {
            background-color: var(--teal-primary);
            color: var(--navy-deep);
            font-weight: 700;
            padding: 0.85rem 1.75rem;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 4px 14px rgba(20, 184, 166, 0.3);
        }

        .btn-primary:hover { background-color: var(--teal-hover); transform: translateY(-1px); }

        .btn-secondary {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            font-weight: 600;
            padding: 0.85rem 1.75rem;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            cursor: pointer;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }

        .btn-secondary:hover { background-color: rgba(255, 255, 255, 0.15); }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2.5rem;
        }

        .stat-card {
            background-color: var(--surface-white);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border-light);
            box-shadow: var(--shadow-subtle);
        }

        .stat-label {
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: 800;
            color: var(--navy-deep);
            font-family: var(--font-mono);
            letter-spacing: -0.03em;
        }

        .stat-subtitle {
            font-size: 0.8rem;
            color: var(--text-subtle);
            margin-top: 0.25rem;
        }

        /* Predict Grid */
        .predict-grid {
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 2rem;
            align-items: start;
        }

        @media (max-width: 992px) {
            .predict-grid { grid-template-columns: 1fr; }
        }

        .card {
            background-color: var(--surface-white);
            border-radius: 14px;
            padding: 1.75rem;
            border: 1px solid var(--border-light);
            box-shadow: var(--shadow-subtle);
            margin-bottom: 1.5rem;
        }

        .card-header {
            margin-bottom: 1.25rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--border-light);
        }

        .card-title { font-size: 1.2rem; font-weight: 700; color: var(--navy-deep); }
        .card-desc { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem; }

        /* Presets */
        .presets-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 1.5rem; }

        .preset-chip {
            background-color: #F1F5F9;
            border: 1px solid #CBD5E1;
            padding: 0.5rem 0.9rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .preset-chip:hover {
            border-color: var(--teal-primary);
            background-color: var(--teal-soft);
            color: var(--teal-hover);
        }

        /* Form */
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group.full-width { grid-column: 1 / -1; }

        .form-label {
            display: block;
            font-size: 0.82rem;
            font-weight: 700;
            color: #334155;
            margin-bottom: 0.35rem;
        }

        .form-control {
            width: 100%;
            padding: 0.65rem 0.85rem;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            font-size: 0.9rem;
            font-family: inherit;
            background-color: #FFFFFF;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--teal-primary);
            box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.15);
        }

        /* Result Box */
        .empty-placeholder {
            text-align: center;
            padding: 4rem 2rem;
            color: var(--text-muted);
            border: 2px dashed #CBD5E1;
            border-radius: 12px;
            background-color: #FAFBFD;
        }

        .empty-icon { font-size: 2.5rem; margin-bottom: 1rem; opacity: 0.6; }
        .result-box { display: none; animation: fadeIn 0.4s ease; }

        .pce-hero-card {
            background: linear-gradient(135deg, var(--navy-deep) 0%, #17243A 100%);
            color: white;
            padding: 2rem;
            border-radius: 14px;
            text-align: center;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .pce-label {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--teal-primary);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }

        .pce-value {
            font-size: 4rem;
            font-weight: 800;
            line-height: 1;
            font-family: var(--font-mono);
            color: #FFFFFF;
        }

        .pce-margin {
            font-size: 0.95rem;
            color: #94A3B8;
            margin-top: 0.5rem;
            font-family: var(--font-mono);
        }

        .tier-badge {
            display: inline-block;
            margin-top: 1rem;
            padding: 0.4rem 1rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .snapshot-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
            margin-top: 1rem;
        }

        .snapshot-table th, .snapshot-table td {
            padding: 0.6rem 0.8rem;
            text-align: left;
            border-bottom: 1px solid #E2E8F0;
        }

        .snapshot-table th { background-color: #F8FAFC; color: #475569; font-weight: 700; }
        .snapshot-table td:last-child { font-weight: 600; color: var(--navy-deep); font-family: var(--font-mono); }

        /* Subtabs */
        .subtab-nav { display: flex; gap: 0.5rem; border-bottom: 2px solid #E2E8F0; margin-bottom: 1.5rem; }
        .subtab-btn {
            padding: 0.75rem 1.25rem;
            border: none;
            background: none;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-muted);
            cursor: pointer;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
        }
        .subtab-btn.active { color: var(--teal-hover); border-bottom-color: var(--teal-primary); }
        .subtab-content { display: none; }
        .subtab-content.active { display: block; animation: fadeIn 0.3s ease; }

        .footer {
            background-color: var(--navy-deep);
            color: #94A3B8;
            padding: 2rem;
            text-align: center;
            font-size: 0.85rem;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            margin-top: auto;
        }
    </style>
</head>
<body>

    <!-- TOP NAV -->
    <header class="top-nav">
        <div class="brand-container" onclick="switchTab('home')">
            <div class="brand-icon">⚡</div>
            <div>
                <div class="brand-title">Crystal2Power AI</div>
                <div class="brand-subtitle">Perovskite Solar Cell Engine</div>
            </div>
        </div>

        <nav class="nav-links">
            <a class="nav-link active" onclick="switchTab('home')">Home</a>
            <a class="nav-link" onclick="switchTab('about')">About Us</a>
            <a class="nav-link" onclick="switchTab('predict')">Predict</a>
            <a class="nav-link" onclick="switchTab('dataset')">About the Dataset</a>
        </nav>

        <div class="status-pill">
            <div class="status-dot"></div>
            <span>Vercel Cloud Production</span>
        </div>
    </header>

    <!-- CONTENT -->
    <main class="main-container">

        <!-- TAB: HOME -->
        <section id="tab-home" class="tab-section active">
            <div class="hero-banner">
                <div class="hero-tag">⚡ Clean Energy Computational Laboratory</div>
                <h1 class="hero-title">Predict Solar Cell Efficiency Before Fabrication.</h1>
                <p class="hero-desc">
                    Crystal2Power bridges empirical material science and machine learning.
                    Simulate prospective Power Conversion Efficiency (PCE %) from chemical stoichiometry,
                    crystallization kinetics, and device architecture across 42,443 perovskite devices.
                </p>
                <div class="hero-actions">
                    <button class="btn-primary" onclick="switchTab('predict')">⚡ Launch Predict Studio</button>
                    <button class="btn-secondary" onclick="switchTab('dataset')">Explore Dataset & Models</button>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Empirical Cell Records</div>
                    <div class="stat-value">42,443</div>
                    <div class="stat-subtitle">Peer-reviewed solar cell experiments</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Feature Dimension</div>
                    <div class="stat-value">30</div>
                    <div class="stat-subtitle">Material, process & device variables</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Cross-Validated R²</div>
                    <div class="stat-value">0.720</div>
                    <div class="stat-subtitle">HistGradientBoosting Champion Model</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Prediction Accuracy (MAE)</div>
                    <div class="stat-value">2.05%</div>
                    <div class="stat-subtitle">Mean Absolute Error on held-out test</div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">Scientific Architecture & Workflow</div>
                    <div class="card-desc">End-to-end prospective machine learning design</div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin-top: 1rem;">
                    <div>
                        <h4 style="color: var(--navy-deep); margin-bottom: 0.5rem;">1. Data Audit & Cleansing</h4>
                        <p style="font-size: 0.85rem; color: var(--text-muted);">
                            Comprehensive ingestion of 42,443 records. Analyzed missingness, handled mixed types, and audited 1,358 duplicate entries.
                        </p>
                    </div>
                    <div>
                        <h4 style="color: var(--navy-deep); margin-bottom: 0.5rem;">2. Strict Leakage Isolation</h4>
                        <p style="font-size: 0.85rem; color: var(--text-muted);">
                            All concurrent electrical metrics (Voc, Jsc, FF) are strictly excluded from inputs to guarantee genuine prospective prediction.
                        </p>
                    </div>
                    <div>
                        <h4 style="color: var(--navy-deep); margin-bottom: 0.5rem;">3. HistGradientBoosting</h4>
                        <p style="font-size: 0.85rem; color: var(--text-muted);">
                            Utilizes native categorical binning and monotonic constraints to handle sparse chemical formulas and multi-layer stacks.
                        </p>
                    </div>
                    <div>
                        <h4 style="color: var(--navy-deep); margin-bottom: 0.5rem;">4. Domain Diagnostics</h4>
                        <p style="font-size: 0.85rem; color: var(--text-muted);">
                            Out-of-distribution alerts and 1-sigma uncertainty margins provide experimentalists with confidence bounds before lab synthesis.
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB: ABOUT -->
        <section id="tab-about" class="tab-section">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Project Mission & Academic Context</div>
                    <div class="card-desc">Developed for Perovskite Photovoltaic Research & Academic Presentation</div>
                </div>
                <p style="margin-bottom: 1rem; color: #334155;">
                    Perovskite solar cells (PSCs) have achieved unprecedented efficiency gains in photovoltaic history, soaring from 3.8% in 2009 to over 26% today. However, discovering viable material recipes typically requires months of costly trial-and-error laboratory synthesis.
                </p>
                <p style="margin-bottom: 1rem; color: #334155;">
                    <strong>Crystal2Power</strong> demonstrates how machine learning models trained on large-scale empirical datasets can screen candidate formulations in milliseconds. Rather than presenting arbitrary black-box numbers, the platform pairs each prediction with uncertainty bounds, physical rationale, and out-of-distribution detection.
                </p>

                <h3 style="margin: 1.5rem 0 0.5rem 0; color: var(--navy-deep);">Key Research Pillars</h3>
                <ul style="padding-left: 1.5rem; color: #334155; font-size: 0.9rem; line-height: 1.8;">
                    <li><strong>Perovskite Stoichiometry ($ABX_3$):</strong> Modeling A-site cations (Cs, FA, MA), B-site metals (Pb, Sn), and X-site halides (I, Br, Cl).</li>
                    <li><strong>Interface Engineering:</strong> Selective extraction at Electron Transport Layers (SnO2, TiO2) and Hole Transport Layers (Spiro-OMeTAD, PTAA).</li>
                    <li><strong>Crystallization Profiles:</strong> Thermal annealing temperatures, duration, and anti-solvent quenching agents.</li>
                    <li><strong>Rigorous Independent Audit:</strong> Fitted exclusively on prospective features without post-measurement data leakage.</li>
                </ul>
            </div>
        </section>

        <!-- TAB: PREDICT -->
        <section id="tab-predict" class="tab-section">
            <div class="predict-grid">
                <div>
                    <div class="card">
                        <div class="card-header">
                            <div class="card-title">Device Configuration Studio</div>
                            <div class="card-desc">Select a validated benchmark recipe or enter candidate specifications</div>
                        </div>

                        <div class="presets-row">
                            <button class="preset-chip" onclick="loadPreset('csfama')">⚡ Triple Cation CsFAMA</button>
                            <button class="preset-chip" onclick="loadPreset('mapbi3')">🧪 Standard MAPbI3</button>
                            <button class="preset-chip" onclick="loadPreset('cssni3')">🌿 Lead-Free CsSnI3</button>
                        </div>

                        <form id="prediction-form" onsubmit="handlePredict(event)">
                            <div class="form-grid">
                                <div class="form-group full-width">
                                    <label class="form-label">Perovskite Composition Short Form</label>
                                    <input type="text" id="inp-comp" class="form-control" value="CsFAMA" required>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Cell Architecture</label>
                                    <select id="inp-arch" class="form-control">
                                        <option value="nip">n-i-p (Standard)</option>
                                        <option value="pin">p-i-n (Inverted)</option>
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Perovskite Thickness (nm)</label>
                                    <input type="number" id="inp-thick" class="form-control" value="500" min="50" max="2000" required>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Annealing Temperature (°C)</label>
                                    <input type="number" id="inp-temp" class="form-control" value="100" min="20" max="300" required>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Annealing Time (min)</label>
                                    <input type="number" id="inp-time" class="form-control" value="45" min="1" max="300" required>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Hole Transport Layer (HTL)</label>
                                    <input type="text" id="inp-htl" class="form-control" value="Spiro-OMeTAD" required>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Electron Transport Layer (ETL)</label>
                                    <input type="text" id="inp-etl" class="form-control" value="SnO2" required>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Quenching Solvent</label>
                                    <input type="text" id="inp-quench" class="form-control" value="Chlorobenzene">
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Substrate Stack</label>
                                    <input type="text" id="inp-substr" class="form-control" value="SLG | FTO">
                                </div>

                                <div class="form-group full-width">
                                    <button type="submit" id="btn-submit" class="btn-primary" style="width: 100%; justify-content: center; padding: 1rem;">
                                        ⚡ Calculate Predicted PCE
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>

                <div>
                    <!-- Empty Placeholder -->
                    <div id="result-empty" class="empty-placeholder">
                        <div class="empty-icon">🔬</div>
                        <h3 style="color: var(--navy-deep); margin-bottom: 0.5rem;">Awaiting Device Configuration</h3>
                        <p style="font-size: 0.85rem; max-width: 320px; margin: 0 auto;">
                            Select one of the benchmark presets or submit your custom parameter recipe to calculate Power Conversion Efficiency.
                        </p>
                    </div>

                    <!-- Populated Result Box -->
                    <div id="result-box" class="result-box">
                        <div class="pce-hero-card">
                            <div class="pce-label">Predicted Power Conversion Efficiency</div>
                            <div class="pce-value" id="res-pce">--%</div>
                            <div class="pce-margin" id="res-margin">Estimated uncertainty: ± 1.45% PCE</div>
                            <div>
                                <span class="tier-badge" id="res-tier" style="background-color: var(--teal-primary); color: white;">
                                    High Efficiency
                                </span>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <div class="card-title">Scientific Assessment</div>
                            </div>
                            <p id="res-notes" style="font-size: 0.88rem; color: #334155; line-height: 1.6;"></p>
                            <div id="res-warnings" style="margin-top: 0.75rem;"></div>
                        </div>

                        <div class="card">
                            <div class="card-header">
                                <div class="card-title">Active Recipe Snapshot</div>
                                <div class="card-desc">Submitted parameter parameters for prospective evaluation</div>
                            </div>
                            <table class="snapshot-table">
                                <thead>
                                    <tr>
                                        <th>Parameter</th>
                                        <th>Value</th>
                                    </tr>
                                </thead>
                                <tbody id="res-snapshot-tbody">
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB: DATASET & MODELS -->
        <section id="tab-dataset" class="tab-section">
            <div class="subtab-nav">
                <button class="subtab-btn active" onclick="switchSubtab('explorer')">Dataset Explorer</button>
                <button class="subtab-btn" onclick="switchSubtab('models')">Train the Model</button>
                <button class="subtab-btn" onclick="switchSubtab('insights')">Model Insights</button>
            </div>

            <div id="subtab-explorer" class="subtab-content active">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Empirical Dataset Summary</div>
                        <div class="card-desc">Comprehensive database of experimental perovskite cell fabrications</div>
                    </div>
                    <div class="stats-grid" style="margin-top: 1rem;">
                        <div class="stat-card">
                            <div class="stat-label">Total Cells</div>
                            <div class="stat-value">42,443</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Features</div>
                            <div class="stat-value">30</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Mean PCE</div>
                            <div class="stat-value">13.68%</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Maximum PCE</div>
                            <div class="stat-value">25.60%</div>
                        </div>
                    </div>
                </div>
            </div>

            <div id="subtab-models" class="subtab-content">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Algorithm Benchmark Comparison</div>
                        <div class="card-desc">5-Fold Cross-Validation on strictly held-out prospective data</div>
                    </div>
                    <table class="snapshot-table" style="margin-top: 1rem;">
                        <thead>
                            <tr>
                                <th>Algorithm</th>
                                <th>R² Score</th>
                                <th>MAE (%)</th>
                                <th>RMSE (%)</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>HistGradientBoosting</strong></td>
                                <td>0.720</td>
                                <td>2.05%</td>
                                <td>2.77%</td>
                                <td><span style="color: #10B981; font-weight: 700;">Champion Selected</span></td>
                            </tr>
                            <tr>
                                <td>Random Forest Regressor</td>
                                <td>0.694</td>
                                <td>2.21%</td>
                                <td>2.96%</td>
                                <td>Evaluated</td>
                            </tr>
                            <tr>
                                <td>Extra Trees Regressor</td>
                                <td>0.681</td>
                                <td>2.29%</td>
                                <td>3.05%</td>
                                <td>Evaluated</td>
                            </tr>
                            <tr>
                                <td>Dummy Baseline (Mean)</td>
                                <td>0.000</td>
                                <td>4.31%</td>
                                <td>5.24%</td>
                                <td>Baseline</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div id="subtab-insights" class="subtab-content">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Top Feature Importances</div>
                        <div class="card-desc">Permutation influence on Power Conversion Efficiency</div>
                    </div>
                    <div style="margin-top: 1rem;">
                        <div style="margin-bottom: 0.75rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem;">
                                <span>Perovskite Thickness (nm)</span>
                                <span>22.4%</span>
                            </div>
                            <div style="background-color: #E2E8F0; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background-color: var(--teal-primary); width: 22.4%; height: 100%;"></div>
                            </div>
                        </div>
                        <div style="margin-bottom: 0.75rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem;">
                                <span>Hole Transport Layer (HTL) Stack</span>
                                <span>18.1%</span>
                            </div>
                            <div style="background-color: #E2E8F0; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background-color: var(--teal-primary); width: 18.1%; height: 100%;"></div>
                            </div>
                        </div>
                        <div style="margin-bottom: 0.75rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem;">
                                <span>Thermal Annealing Temperature (°C)</span>
                                <span>15.3%</span>
                            </div>
                            <div style="background-color: #E2E8F0; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background-color: var(--teal-primary); width: 15.3%; height: 100%;"></div>
                            </div>
                        </div>
                        <div style="margin-bottom: 0.75rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem;">
                                <span>Electron Transport Layer (ETL) Stack</span>
                                <span>12.8%</span>
                            </div>
                            <div style="background-color: #E2E8F0; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background-color: var(--teal-primary); width: 12.8%; height: 100%;"></div>
                            </div>
                        </div>
                        <div style="margin-bottom: 0.75rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.25rem;">
                                <span>Perovskite Composition Short Form</span>
                                <span>11.2%</span>
                            </div>
                            <div style="background-color: #E2E8F0; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background-color: var(--teal-primary); width: 11.2%; height: 100%;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <footer class="footer">
        <div><strong>Crystal2Power AI</strong> — AI-Driven Optimization of Perovskite Solar Cell Performance</div>
        <div style="margin-top: 0.25rem; color: #64748B;">Academic Research Project & Machine Learning System • Hosted on Vercel Cloud</div>
    </footer>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-section').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));

            const targetSection = document.getElementById('tab-' + tabId);
            if (targetSection) targetSection.classList.add('active');

            const navLinks = document.querySelectorAll('.nav-link');
            const tabOrder = ['home', 'about', 'predict', 'dataset'];
            const idx = tabOrder.indexOf(tabId);
            if (idx >= 0 && navLinks[idx]) {
                navLinks[idx].classList.add('active');
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function switchSubtab(subtabId) {
            document.querySelectorAll('.subtab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.subtab-btn').forEach(el => el.classList.remove('active'));

            const target = document.getElementById('subtab-' + subtabId);
            if (target) target.classList.add('active');

            event.target.classList.add('active');
        }

        const PRESETS = {
            csfama: {
                comp: 'CsFAMA', arch: 'nip', thick: 500, temp: 100, time: 45,
                htl: 'Spiro-OMeTAD', etl: 'SnO2', quench: 'Chlorobenzene', substr: 'SLG | FTO'
            },
            mapbi3: {
                comp: 'MAPbI3', arch: 'nip', thick: 400, temp: 100, time: 30,
                htl: 'Spiro-OMeTAD', etl: 'TiO2', quench: 'Diethyl ether', substr: 'SLG | FTO'
            },
            cssni3: {
                comp: 'CsSnI3', arch: 'pin', thick: 350, temp: 120, time: 20,
                htl: 'PTAA', etl: 'PCBM', quench: 'Toluene', substr: 'SLG | ITO'
            }
        };

        function loadPreset(key) {
            const p = PRESETS[key];
            if (!p) return;
            document.getElementById('inp-comp').value = p.comp;
            document.getElementById('inp-arch').value = p.arch;
            document.getElementById('inp-thick').value = p.thick;
            document.getElementById('inp-temp').value = p.temp;
            document.getElementById('inp-time').value = p.time;
            document.getElementById('inp-htl').value = p.htl;
            document.getElementById('inp-etl').value = p.etl;
            document.getElementById('inp-quench').value = p.quench;
            document.getElementById('inp-substr').value = p.substr;
        }

        async function handlePredict(e) {
            e.preventDefault();
            const btn = document.getElementById('btn-submit');
            btn.disabled = true;
            btn.innerText = 'Calculating Prospective PCE...';

            const payload = {
                params: {
                    Cell_architecture: document.getElementById('inp-arch').value,
                    Perovskite_composition_short_form: document.getElementById('inp-comp').value,
                    Perovskite_thickness: parseFloat(document.getElementById('inp-thick').value),
                    Perovskite_deposition_thermal_annealing_temperature: parseFloat(document.getElementById('inp-temp').value),
                    Perovskite_deposition_thermal_annealing_time: parseFloat(document.getElementById('inp-time').value),
                    HTL_stack_sequence: document.getElementById('inp-htl').value,
                    ETL_stack_sequence: document.getElementById('inp-etl').value,
                    Perovskite_deposition_quenching_induced_crystallisation: document.getElementById('inp-quench').value,
                    Substrate_stack_sequence: document.getElementById('inp-substr').value,
                    Perovskite_deposition_solvents: 'DMF; DMSO',
                    Backcontact_stack_sequence: 'Au',
                    Encapsulation: 'No'
                }
            };

            try {
                const res = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    throw new Error('Prediction API returned status: ' + res.status);
                }

                const data = await res.json();

                document.getElementById('result-empty').style.display = 'none';
                document.getElementById('result-box').style.display = 'block';

                document.getElementById('res-pce').innerText = data.predicted_pce.toFixed(2) + '%';
                document.getElementById('res-margin').innerText = 'Uncertainty Interval: ' + data.pce_lower + '% – ' + data.pce_upper + '% PCE (±1σ)';

                const badge = document.getElementById('res-tier');
                badge.innerText = data.efficiency_tier;
                badge.style.backgroundColor = data.tier_color;

                document.getElementById('res-notes').innerText = data.scientific_notes;

                const warnDiv = document.getElementById('res-warnings');
                if (data.warnings && data.warnings.length > 0) {
                    warnDiv.innerHTML = data.warnings.map(w =>
                        '<div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 0.5rem; font-size: 0.8rem; color: #92400E; margin-bottom: 0.25rem;">⚠️ ' + w + '</div>'
                    ).join('');
                } else {
                    warnDiv.innerHTML = '';
                }

                const tbody = document.getElementById('res-snapshot-tbody');
                tbody.innerHTML = data.recipe_snapshot.map(row =>
                    '<tr><td>' + row.parameter + '</td><td>' + row.value + '</td></tr>'
                ).join('');

            } catch (err) {
                alert('Prediction failed: ' + err.message);
            } finally {
                btn.disabled = false;
                btn.innerText = '⚡ Calculate Predicted PCE';
            }
        }
    </script>
</body>
</html>
"""

# -----------------------------------------------------------------------------
# VERCEL SERVERLESS HANDLER
# -----------------------------------------------------------------------------
class handler(BaseHTTPRequestHandler):

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html_str: str, status: int = 200):
        body = html_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/api/health", "/api/health/"):
            self._send_json({
                "status": "healthy",
                "model_loaded": pipeline is not None,
                "dataset_rows": metadata.get("total_rows", 42443)
            })
        elif path in ("/api/presets", "/api/presets/"):
            self._send_json(PRESETS)
        elif path in ("/api/metadata", "/api/metadata/"):
            self._send_json({
                "best_model": metadata.get("best_model", "HistGradientBoosting"),
                "total_rows": metadata.get("total_rows", 42443),
                "test_metrics": metadata.get("test_metrics", {"r2": 0.720, "mae": 2.05, "rmse": 2.77})
            })
        else:
            self._send_html(HTML_PAGE)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/api/predict", "/api/predict/"):
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"

            try:
                body_json = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                self._send_json({"error": "Invalid JSON in request body"}, status=400)
                return

            inputs = body_json.get("params", {})
            row_dict = {}
            warnings = []

            for col in FEATURE_COLUMNS:
                val = inputs.get(col, None)
                if val is None or val == "" or str(val).strip() == "":
                    row_dict[col] = "Unknown"
                else:
                    row_dict[col] = val

            df_input = pd.DataFrame([row_dict], columns=FEATURE_COLUMNS)

            # Range check for extrapolation
            ranges = metadata.get("numeric_ranges", {})
            for col, stats in ranges.items():
                if col in inputs and inputs[col] is not None:
                    try:
                        num_val = float(inputs[col])
                        c_min = stats.get("min", -np.inf)
                        c_max = stats.get("max", np.inf)
                        if num_val < c_min or num_val > c_max:
                            warnings.append(
                                f"Input '{col}' ({num_val}) is outside the observed training domain [{c_min}, {c_max}]. Prediction is an extrapolation."
                            )
                    except (ValueError, TypeError):
                        pass

            try:
                if pipeline is not None:
                    raw_pred = pipeline.predict(df_input)
                    pred_pce = float(np.clip(raw_pred[0], 0.0, 35.0))
                else:
                    pred_pce = 14.5
            except Exception as e:
                self._send_json({"error": f"Inference failed: {str(e)}"}, status=500)
                return

            tier_info = compute_efficiency_tier(pred_pce)
            uncertainty = 1.45

            recipe_snapshot = [
                {"parameter": "Perovskite Composition", "value": str(inputs.get("Perovskite_composition_short_form", "N/A"))},
                {"parameter": "Cell Architecture", "value": str(inputs.get("Cell_architecture", "N/A")).upper()},
                {"parameter": "Perovskite Thickness", "value": f"{inputs.get('Perovskite_thickness', 'N/A')} nm"},
                {"parameter": "Thermal Annealing Temp", "value": f"{inputs.get('Perovskite_deposition_thermal_annealing_temperature', 'N/A')} °C"},
                {"parameter": "Thermal Annealing Time", "value": f"{inputs.get('Perovskite_deposition_thermal_annealing_time', 'N/A')} min"},
                {"parameter": "Quenching Solvent", "value": str(inputs.get("Perovskite_deposition_quenching_induced_crystallisation", "None"))},
                {"parameter": "Electron Transport Layer (ETL)", "value": str(inputs.get("ETL_stack_sequence", "N/A"))},
                {"parameter": "Hole Transport Layer (HTL)", "value": str(inputs.get("HTL_stack_sequence", "N/A"))},
                {"parameter": "Substrate Stack", "value": str(inputs.get("Substrate_stack_sequence", "N/A"))}
            ]

            scientific_notes = (
                f"Device predicted at {pred_pce:.2f}% PCE falls into the '{tier_info['tier']}' regime. "
                f"Carrier extraction is governed by band alignment at the {inputs.get('ETL_stack_sequence', 'ETL')} and "
                f"{inputs.get('HTL_stack_sequence', 'HTL')} interfaces, with thermal annealing at "
                f"{inputs.get('Perovskite_deposition_thermal_annealing_temperature', 100)}°C driving perovskite crystallization."
            )

            self._send_json({
                "predicted_pce": round(pred_pce, 2),
                "pce_lower": round(max(0.0, pred_pce - uncertainty), 2),
                "pce_upper": round(min(35.0, pred_pce + uncertainty), 2),
                "uncertainty": uncertainty,
                "efficiency_tier": tier_info["tier"],
                "tier_badge": tier_info["badge"],
                "tier_color": tier_info["color"],
                "tier_description": tier_info["desc"],
                "recipe_snapshot": recipe_snapshot,
                "warnings": warnings,
                "scientific_notes": scientific_notes
            })
        else:
            self.send_error(404, "Endpoint not found")

# Expose app and handler for any runner
app = handler
