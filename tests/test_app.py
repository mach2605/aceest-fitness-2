import json
import pytest
from app import app, CATEGORIES

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_index_page(client):
    rv = client.get('/')
    assert rv.status_code == 200
    for cat in CATEGORIES:
        assert cat.encode() in rv.data


def test_add_and_view_workout(client):
    # Add a valid workout
    rv = client.post('/add', data={
        'category': 'Workout',
        'exercise': 'Push-ups',
        'duration': '20'
    }, follow_redirects=True)
    assert rv.status_code == 200

    # View workouts
    rv = client.get('/view')
    assert rv.status_code == 200
    assert b'Push-ups' in rv.data


def test_api_workouts_structure(client):
    rv = client.get('/api/workouts')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, dict)
    for cat in CATEGORIES:
        assert cat in data
        assert isinstance(data[cat], list)


def test_api_summary(client):
    rv = client.get('/api/summary')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'total_time' in data
    assert 'message' in data
    assert 'version' in data
    assert data['version'] == '1.2'


def test_health_check(client):
    rv = client.get('/api/health')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'healthy'

def test_api_charts(client):
    rv = client.get('/api/charts')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'Warm-up' in data
    assert isinstance(data['Workout'], list)


def test_api_diet(client):
    rv = client.get('/api/diet')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'Weight Loss' in data
    assert isinstance(data['Muscle Gain'], list)


def test_charts_page(client):
    rv = client.get('/charts')
    assert rv.status_code == 200
    assert b'Workout Chart' in rv.data or b'Warm-up' in rv.data


def test_diet_page(client):
    rv = client.get('/diet')
    assert rv.status_code == 200
    assert b'Diet' in rv.data
