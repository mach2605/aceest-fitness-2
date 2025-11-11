import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'ACEestFitness' in rv.data

def test_charts_page(client):
    rv = client.get('/charts')
    assert rv.status_code == 200

def test_diet_page(client):
    rv = client.get('/diet')
    assert rv.status_code == 200

def test_user_page(client):
    rv = client.get('/user')
    assert rv.status_code == 200

def test_api_health(client):
    rv = client.get('/api/health')
    assert rv.status_code == 200

def test_api_progress(client):
    rv = client.get('/api/progress')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'totals' in data
