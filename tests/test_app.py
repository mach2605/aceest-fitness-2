import json
import os
import sys
import tempfile
import pytest

# Ensure project root is on sys.path so tests can import the app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_page(client):
    rv = client.get('/')
    assert rv.status_code == 200


def test_api_get_workouts(client):
    rv = client.get('/api/workouts')
    assert rv.status_code == 200
    data = rv.get_json()
    # app may return a list (v1 converted app) or a dict (multi-category app). Accept both.
    assert isinstance(data, (list, dict))
