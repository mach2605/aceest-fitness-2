from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pathlib import Path
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = "change-this-secret-for-prod"

DATA_FILE = Path(__file__).parent / "data/workouts.json"

CATEGORIES = ["Warm-up", "Workout", "Cool-down"]


def load_workouts():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {cat: [] for cat in CATEGORIES}


def save_workouts(workouts):
    DATA_FILE.write_text(json.dumps(workouts, indent=2), encoding="utf-8")


@app.route("/")
def index():
    """Show the form to add a categorized exercise."""
    return render_template("index.html", categories=CATEGORIES)


@app.route("/add", methods=["POST"])
def add_workout():
    category = request.form.get("category", "").strip()
    exercise = request.form.get("exercise", "").strip()
    duration_str = request.form.get("duration", "").strip()

    if not exercise or not duration_str:
        flash("Please enter both exercise and duration.", "error")
        return redirect(url_for("index"))

    if category not in CATEGORIES:
        flash("Invalid category selected.", "error")
        return redirect(url_for("index"))

    try:
        duration = int(duration_str)
        if duration <= 0:
            raise ValueError
    except ValueError:
        flash("Duration must be a positive integer.", "error")
        return redirect(url_for("index"))

    workouts = load_workouts()
    entry = {
        "exercise": exercise,
        "duration": duration,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    workouts.setdefault(category, []).append(entry)
    save_workouts(workouts)

    flash(f"{exercise} added to {category} category successfully!", "success")
    return redirect(url_for("index"))


@app.route("/view")
def view_workouts():
    workouts = load_workouts()
    total_time = sum(
        entry["duration"] for sessions in workouts.values() for entry in sessions
    )

    if total_time < 30:
        message = "Good start! Keep moving 💪"
    elif total_time < 60:
        message = "Nice effort! You're building consistency 🔥"
    else:
        message = "Excellent dedication! Keep up the great work 🏆"

    return render_template(
        "view.html",
        workouts=workouts,
        total_time=total_time,
        message=message,
    )


@app.route("/api/workouts", methods=["GET"])
def api_get_workouts():
    return jsonify(load_workouts())


@app.route("/api/summary", methods=["GET"])
def api_summary():
    workouts = load_workouts()
    total_time = sum(
        entry["duration"] for sessions in workouts.values() for entry in sessions
    )

    if total_time < 30:
        msg = "Good start! Keep moving 💪"
    elif total_time < 60:
        msg = "Nice effort! You're building consistency 🔥"
    else:
        msg = "Excellent dedication! Keep up the great work 🏆"

    return jsonify(
        {
            "total_time": total_time,
            "message": msg,
            "timestamp": datetime.now().isoformat(),
            "version": "1.2",
        }
    )


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(
        {"status": "healthy", "version": "1.2", "timestamp": datetime.now().isoformat()}
    )


if __name__ == "__main__":
    if not DATA_FILE.exists():
        save_workouts({cat: [] for cat in CATEGORIES})
    app.run(host="0.0.0.0", port=5001, debug=True)
