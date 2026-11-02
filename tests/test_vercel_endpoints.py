"""Integration tests for Vercel Serverless Entrypoint endpoints and routing."""

import io
import json
import pytest
import app

def test_vercel_health_with_rewrite_query():
    """Simulate Vercel internal rewrite with query param: /api/index.py?__route=/api/health"""
    h = app.handler.__new__(app.handler)
    h.path = '/api/index.py?__route=/api/health'
    h.headers = {}
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_GET()
    res = json.loads(h.wfile.getvalue().decode('utf-8'))
    assert res['status'] == 'healthy'
    assert res['model_loaded'] is True
    assert res['dataset_rows'] == 42443

def test_vercel_presets_with_rewrite_query():
    """Simulate Vercel internal rewrite: /api/index.py?__route=/api/presets"""
    h = app.handler.__new__(app.handler)
    h.path = '/api/index.py?__route=/api/presets'
    h.headers = {}
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_GET()
    res = json.loads(h.wfile.getvalue().decode('utf-8'))
    assert 'csfama' in res
    assert 'mapbi3' in res
    assert 'cssni3' in res

def test_vercel_metadata_with_rewrite_query():
    """Simulate Vercel internal rewrite: /api/index.py?__route=/api/metadata"""
    h = app.handler.__new__(app.handler)
    h.path = '/api/index.py?__route=/api/metadata'
    h.headers = {}
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_GET()
    res = json.loads(h.wfile.getvalue().decode('utf-8'))
    assert res['best_model'] == 'HistGradientBoosting'
    assert 'r2' in res['test_metrics']
    assert res['test_metrics']['r2'] > 0

def test_vercel_predict_with_rewrite_query_recipe1():
    """Simulate Vercel rewrite with Recipe 1 (Triple Cation CsFAMA)."""
    h = app.handler.__new__(app.handler)
    h.path = '/api/index.py?__route=/api/predict'
    payload = json.dumps({
        'params': {
            'Cell_architecture': 'nip',
            'Perovskite_composition_short_form': 'CsFAMA',
            'Perovskite_thickness': 500,
            'Perovskite_deposition_thermal_annealing_temperature': 100,
            'Perovskite_deposition_thermal_annealing_time': 45,
            'ETL_stack_sequence': 'SnO2',
            'HTL_stack_sequence': 'Spiro-OMeTAD',
            'Perovskite_deposition_quenching_induced_crystallisation': 'Chlorobenzene',
            'Substrate_stack_sequence': 'SLG | FTO'
        }
    }).encode('utf-8')
    h.headers = {'Content-Length': str(len(payload))}
    h.rfile = io.BytesIO(payload)
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_POST()
    res = json.loads(h.wfile.getvalue().decode('utf-8'))
    assert 'predicted_pce' in res
    assert 'efficiency_tier' in res
    assert res['predicted_pce'] > 0  # Real model inference produced prospective PCE
    assert 'recipe_snapshot' in res
    assert len(res['recipe_snapshot']) == 9

def test_vercel_predict_with_rewrite_query_recipe2():
    """Simulate Vercel rewrite with Recipe 2 (Standard MAPbI3)."""
    h = app.handler.__new__(app.handler)
    h.path = '/api/index.py?__route=/api/predict'
    payload = json.dumps({
        'params': {
            'Cell_architecture': 'nip',
            'Perovskite_composition_short_form': 'MAPbI3',
            'Perovskite_thickness': 400,
            'Perovskite_deposition_thermal_annealing_temperature': 100,
            'Perovskite_deposition_thermal_annealing_time': 30,
            'ETL_stack_sequence': 'TiO2',
            'HTL_stack_sequence': 'Spiro-OMeTAD',
            'Perovskite_deposition_quenching_induced_crystallisation': 'Diethyl ether',
            'Substrate_stack_sequence': 'SLG | FTO'
        }
    }).encode('utf-8')
    h.headers = {'Content-Length': str(len(payload))}
    h.rfile = io.BytesIO(payload)
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_POST()
    res = json.loads(h.wfile.getvalue().decode('utf-8'))
    assert 'predicted_pce' in res
    assert 'efficiency_tier' in res
    assert res['predicted_pce'] > 0

def test_vercel_predict_via_matched_path_header():
    """Simulate Vercel infrastructure header x-matched-path: /api/predict"""
    h = app.handler.__new__(app.handler)
    h.path = '/api/index.py'  # Path is rewritten without query
    payload = json.dumps({
        'params': {
            'Cell_architecture': 'pin',
            'Perovskite_composition_short_form': 'CsSnI3',
            'Perovskite_thickness': 350,
            'Perovskite_deposition_thermal_annealing_temperature': 120,
            'ETL_stack_sequence': 'PCBM',
            'HTL_stack_sequence': 'PTAA'
        }
    }).encode('utf-8')
    h.headers = {
        'Content-Length': str(len(payload)),
        'x-matched-path': '/api/predict'
    }
    h.rfile = io.BytesIO(payload)
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_POST()
    res = json.loads(h.wfile.getvalue().decode('utf-8'))
    assert 'predicted_pce' in res
    assert res['predicted_pce'] > 0

def test_vercel_unknown_endpoint_returns_json_404():
    """Verify unknown /api/* endpoints return 404 JSON instead of falling back to HTML."""
    h = app.handler.__new__(app.handler)
    h.path = '/api/index.py?__route=/api/nonexistent'
    h.headers = {}
    h.wfile = io.BytesIO()
    response_code = []
    h.send_response = lambda code: response_code.append(code)
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_GET()
    res = json.loads(h.wfile.getvalue().decode('utf-8'))
    assert res['status'] == 404
    assert 'not found' in res['error'].lower()
    assert response_code == [404]

def test_vercel_spa_frontend_endpoint():
    """Verify root GET serves the full Crystal2Power frontend."""
    h = app.handler.__new__(app.handler)
    h.path = '/api/index.py?__route=/'
    h.headers = {}
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_GET()
    html_out = h.wfile.getvalue().decode('utf-8')
    assert '<title>Crystal2Power AI' in html_out
    assert 'Calculate Predicted PCE' in html_out
