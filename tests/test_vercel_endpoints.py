"""Integration tests for Vercel Serverless Entrypoint endpoints."""

import io
import json
import pytest
import app

def test_vercel_health_endpoint():
    h = app.handler.__new__(app.handler)
    h.path = '/api/health'
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_GET()
    res = json.loads(h.wfile.getvalue().decode('utf-8'))
    assert res['status'] == 'healthy'
    assert res['model_loaded'] is True
    assert res['dataset_rows'] == 42443

def test_vercel_presets_endpoint():
    h = app.handler.__new__(app.handler)
    h.path = '/api/presets'
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_GET()
    res = json.loads(h.wfile.getvalue().decode('utf-8'))
    assert 'csfama' in res
    assert 'mapbi3' in res
    assert 'cssni3' in res

def test_vercel_metadata_endpoint():
    h = app.handler.__new__(app.handler)
    h.path = '/api/metadata'
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_GET()
    res = json.loads(h.wfile.getvalue().decode('utf-8'))
    assert res['best_model'] == 'HistGradientBoosting'
    assert 'r2' in res['test_metrics']
    assert res['test_metrics']['r2'] > 0


def test_vercel_predict_endpoint():
    h = app.handler.__new__(app.handler)
    h.path = '/api/predict'
    payload = json.dumps({
        'params': {
            'Cell_architecture': 'nip',
            'Perovskite_composition_short_form': 'CsFAMA',
            'Perovskite_thickness': 500,
            'Perovskite_deposition_thermal_annealing_temperature': 100,
            'ETL_stack_sequence': 'SnO2',
            'HTL_stack_sequence': 'Spiro-OMeTAD'
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
    assert len(res['recipe_snapshot']) > 0

def test_vercel_spa_frontend_endpoint():
    h = app.handler.__new__(app.handler)
    h.path = '/'
    h.wfile = io.BytesIO()
    h.send_response = lambda code: None
    h.send_header = lambda k, v: None
    h.end_headers = lambda: None
    h.do_GET()
    html_out = h.wfile.getvalue().decode('utf-8')
    assert '<title>Crystal2Power AI' in html_out
    assert 'Calculate Predicted PCE' in html_out
    assert 'Triple Cation CsFAMA' in html_out
