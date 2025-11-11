from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from pathlib import Path
from datetime import datetime
import json, io, os

# optional PDF support (reportlab)
try:
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors as rl_colors
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'change-this-secret-for-prod'

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
USER_FILE = DATA_DIR / 'user_info.json'
WORKOUTS_FILE = DATA_DIR / 'workouts.json'

CATEGORIES = ["Warm-up", "Workout", "Cool-down"]
MET_VALUES = {"Warm-up": 3, "Workout": 6, "Cool-down": 2.5}

def load_user():
    if USER_FILE.exists():
        try:
            return json.loads(USER_FILE.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}

def save_user(user):
    USER_FILE.write_text(json.dumps(user, indent=2), encoding='utf-8')

def load_workouts():
    if WORKOUTS_FILE.exists():
        try:
            return json.loads(WORKOUTS_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {cat: [] for cat in CATEGORIES}

def save_workouts(workouts):
    WORKOUTS_FILE.write_text(json.dumps(workouts, indent=2), encoding='utf-8')

# --- Routes ---
@app.route('/')
def index():
    user = load_user()
    return render_template('index.html', categories=CATEGORIES, user=user)

@app.route('/user', methods=['GET','POST'])
def user_info():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        regn = request.form.get('regn','').strip()
        try:
            age = int(request.form.get('age','0'))
            gender = request.form.get('gender','').strip().upper()
            height_cm = float(request.form.get('height','0'))
            weight_kg = float(request.form.get('weight','0'))
        except Exception:
            flash('Invalid numeric values provided.', 'error')
            return redirect(url_for('user_info'))
        if height_cm <=0 or weight_kg <=0 or age<=0:
            flash('Age/height/weight must be positive.', 'error')
            return redirect(url_for('user_info'))
        bmi = weight_kg / ((height_cm/100)**2)
        if gender == 'M':
            bmr = 10*weight_kg + 6.25*height_cm - 5*age + 5
        else:
            bmr = 10*weight_kg + 6.25*height_cm - 5*age - 161
        user = {
            'name': name, 'regn_id': regn, 'age': age, 'gender': gender,
            'height': height_cm, 'weight': weight_kg, 'bmi': round(bmi,1), 'bmr': int(round(bmr)),
            'weekly_cal_goal': 2000
        }
        save_user(user)
        flash('User info saved!', 'success')
        return redirect(url_for('index'))
    else:
        user = load_user()
        return render_template('user.html', user=user)

@app.route('/add', methods=['POST'])
def add_workout():
    category = request.form.get('category','').strip()
    exercise = request.form.get('exercise','').strip()
    duration_str = request.form.get('duration','').strip()
    if not exercise or not duration_str:
        flash('Please enter exercise and duration.', 'error')
        return redirect(url_for('index'))
    try:
        duration = int(duration_str)
        if duration <= 0:
            raise ValueError
    except ValueError:
        flash('Duration must be a positive integer.', 'error')
        return redirect(url_for('index'))
    if category not in CATEGORIES:
        flash('Invalid category.', 'error')
        return redirect(url_for('index'))

    user = load_user()
    weight = user.get('weight', 70)
    met = MET_VALUES.get(category, 5)
    calories = (met * 3.5 * weight / 200) * duration

    entry = {
        'exercise': exercise,
        'duration': duration,
        'calories': round(calories,1),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    workouts = load_workouts()
    workouts.setdefault(category, []).append(entry)
    save_workouts(workouts)
    flash(f"{exercise} added to {category} ({duration} min).", 'success')
    return redirect(url_for('index'))

@app.route('/view')
def view_workouts():
    workouts = load_workouts()
    total_time = sum(entry['duration'] for sessions in workouts.values() for entry in sessions)
    total_cal = sum(entry.get('calories',0) for sessions in workouts.values() for entry in sessions)
    if total_time < 30:
        message = 'Good start! Keep moving 💪'
    elif total_time < 60:
        message = "Nice effort! You're building consistency 🔥"
    else:
        message = 'Excellent dedication! Keep up the great work 🏆'
    return render_template('view.html', workouts=workouts, total_time=total_time, total_cal=round(total_cal,1), message=message)

@app.route('/charts')
def charts_page():
    return render_template('charts.html', charts=WORKOUT_CHARTS)

@app.route('/diet')
def diet_page():
    return render_template('diet.html', diets=DIET_PLANS)

@app.route('/progress')
def progress_page():
    return render_template('progress.html')

@app.route('/export')
def export_pdf():
    if not REPORTLAB_AVAILABLE:
        flash('PDF export requires reportlab library. Install it with pip.', 'error')
        return redirect(url_for('view_workouts'))
    user = load_user()
    if not user:
        flash('Please save user info before exporting report.', 'error')
        return redirect(url_for('user_info'))
    workouts = load_workouts()
    buffer = io.BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    c.setFont('Helvetica-Bold', 16)
    c.drawString(50, h-50, f"Weekly Fitness Report - {user.get('name','User')}")
    c.setFont('Helvetica', 11)
    c.drawString(50, h-80, f"Regn-ID: {user.get('regn_id','-')} | Age: {user.get('age','-')} | Gender: {user.get('gender','-')}")
    c.drawString(50, h-100, f"Height: {user.get('height','-')} cm | Weight: {user.get('weight','-')} kg | BMI: {user.get('bmi','-')} | BMR: {user.get('bmr','-')} kcal/day")
    y = h-140
    table_data = [["Category","Exercise","Duration(min)","Calories(kcal)","Date"]]
    for cat, sessions in workouts.items():
        for e in sessions:
            table_data.append([cat, e['exercise'], str(e['duration']), f"{e.get('calories',0):.1f}", e['timestamp'].split()[0]])
    table = Table(table_data, colWidths=[70,180,80,80,80])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),rl_colors.lightblue),('GRID',(0,0),(-1,-1),0.5,rl_colors.black)]))
    table.wrapOn(c, w-100, y)
    table.drawOn(c,50,y-20)
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{user.get('name','user')}_weekly_report.pdf", mimetype='application/pdf')

# APIs
@app.route('/api/user', methods=['GET','POST'])
def api_user():
    if request.method == 'GET':
        return jsonify(load_user())
    else:
        data = request.get_json() or {}
        if not data.get('name'):
            return jsonify({'error':'name required'}), 400
        save_user(data)
        return jsonify({'status':'ok'})

@app.route('/api/workouts', methods=['GET'])
def api_workouts():
    return jsonify(load_workouts())

@app.route('/api/progress', methods=['GET'])
def api_progress():
    workouts = load_workouts()
    totals = {cat: sum(e['duration'] for e in sessions) for cat, sessions in workouts.items()}
    total_minutes = sum(totals.values())
    return jsonify({'totals': totals, 'total_minutes': total_minutes})

@app.route('/api/charts', methods=['GET'])
def api_charts():
    return jsonify(WORKOUT_CHARTS)

@app.route('/api/diet', methods=['GET'])
def api_diet():
    return jsonify(DIET_PLANS)

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({'status':'healthy','version':'1.2.1','timestamp': datetime.now().isoformat()})

# static data
WORKOUT_CHARTS = {
    "Warm-up": ["5 min Jog", "Jumping Jacks", "Arm Circles", "Leg Swings", "Dynamic Stretching"],
    "Workout": ["Push-ups", "Squats", "Plank", "Lunges", "Burpees", "Crunches"],
    "Cool-down": ["Slow Walking", "Static Stretching", "Deep Breathing", "Yoga Poses"]
}
DIET_PLANS = {
    "Weight Loss": ["Oatmeal with Fruits", "Grilled Chicken Salad", "Vegetable Soup", "Brown Rice & Stir-fry Veggies"],
    "Muscle Gain": ["Egg Omelet", "Chicken Breast", "Quinoa & Beans", "Protein Shake", "Greek Yogurt with Nuts"],
    "Endurance": ["Banana & Peanut Butter", "Whole Grain Pasta", "Sweet Potatoes", "Salmon & Avocado", "Trail Mix"]
}

if __name__ == '__main__':
    if not USER_FILE.exists(): save_user({})
    if not WORKOUTS_FILE.exists(): save_workouts({cat:[] for cat in CATEGORIES})
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
