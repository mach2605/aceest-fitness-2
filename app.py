from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-for-prod"

DATA_FILE = Path(__file__).parent / 'workouts_v1.json'


def load_workouts():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding='utf-8'))
        except Exception:
            return []
    return []


def save_workouts(workouts):
    DATA_FILE.write_text(json.dumps(workouts, indent=2), encoding='utf-8')


@app.route('/')
def index():
    """Show a simple form to add workouts and a link to view them."""
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add_workout():
    workout = request.form.get('workout', '').strip()
    duration_str = request.form.get('duration', '').strip()

    if not workout or not duration_str:
        flash('Please enter both workout and duration.', 'error')
        return redirect(url_for('index'))

    try:
        duration = int(duration_str)
        if duration <= 0:
            raise ValueError('Duration must be positive')
    except ValueError:
        flash('Duration must be a positive integer.', 'error')
        return redirect(url_for('index'))

    workouts = load_workouts()
    workouts.append({'workout': workout, 'duration': duration})
    save_workouts(workouts)

    flash(f"'{workout}' added successfully!", 'success')
    return redirect(url_for('index'))


@app.route('/view')
def view_workouts():
    workouts = load_workouts()
    return render_template('view.html', workouts=workouts)


@app.route('/api/workouts', methods=['GET'])
def api_get_workouts():
    return jsonify(load_workouts())

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'version': '1.1',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Ensure data file exists
    if not DATA_FILE.exists():
        save_workouts([])

    app.run(host='0.0.0.0', port=5001, debug=True)
