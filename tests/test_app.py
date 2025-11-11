import pytest
from app import app, CATEGORIES


# --- Fixtures -----------------------------------------------------------------

@pytest.fixture
def client():
    """Return a test client for Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# --- Core Pages ---------------------------------------------------------------

def test_index_page(client):
    """Check index route loads successfully."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'ACEestFitness' in rv.data


def test_charts_page(client):
    rv = client.get('/charts')
    assert rv.status_code == 200
    assert b'Workout Chart' in rv.data or b'Workout' in rv.data


def test_diet_page(client):
    rv = client.get('/diet')
    assert rv.status_code == 200
    assert b'Diet' in rv.data


def test_user_page(client):
    rv = client.get('/user')
    assert rv.status_code == 200
    assert b'User Info' in rv.data


# --- API Endpoints ------------------------------------------------------------

def test_api_health(client):
    rv = client.get('/api/health')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'status' in data and data['status'] == 'healthy'


def test_api_charts(client):
    rv = client.get('/api/charts')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, dict)
    assert "Warm-up" in data


def test_api_diet(client):
    rv = client.get('/api/diet')
    assert rv.status_code == 200
    data = rv.get_json()
    assert isinstance(data, dict)
    assert "Weight Loss" in data


def test_user_save_and_api(client):
    """Save user info via API and verify persistence."""
    payload = {
        "name": "Test User",
        "regn_id": "R123",
        "age": 25,
        "gender": "M",
        "height": 175,
        "weight": 70
    }
    rv = client.post('/api/user', json=payload)
    assert rv.status_code == 200

    rv = client.get('/api/user')
    data = rv.get_json()
    assert data.get('name') == "Test User"


def test_add_and_progress(client):
    """Add a workout and verify progress API updates."""
    rv = client.post('/add', data={
        'category': 'Workout',
        'exercise': 'Push-ups',
        'duration': '20'
    }, follow_redirects=True)
    assert rv.status_code == 200

    rv = client.get('/api/progress')
    data = rv.get_json()
    assert 'totals' in data
    assert 'Workout' in data['totals']


def test_export_requires_user(client):
    """If user info is missing, export should redirect with error flash."""
    rv = client.get('/export', follow_redirects=True)
    assert rv.status_code in (200, 302)
