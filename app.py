"""
RespectCircle Flask App (Single User, Single Page)
--------------------------------------------------
A web application to visualize and edit activity goals and progress using animated rings.
"""

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import logging
import os, subprocess

# --- App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///respectcircle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Model ---
class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weekly_goal = db.Column(db.Integer, default=300, nullable=False)
    daily_goal = db.Column(db.Integer, default=60, nullable=False)
    monthly_goal = db.Column(db.Integer, default=1200, nullable=False)
    weekly_played = db.Column(db.Integer, default=0, nullable=False)
    daily_played = db.Column(db.Integer, default=0, nullable=False)
    monthly_played = db.Column(db.Integer, default=0, nullable=False)
    high_score = db.Column(db.Integer, default=0, nullable=False)

# --- DB Initialization ---
def init_db():
    with app.app_context():
        db.create_all()
        if not Metric.query.first():
            db.session.add(Metric())
            db.session.commit()
init_db()

# --- Main Page ---
@app.route('/', methods=['GET'])
def dashboard():
    metrics = Metric.query.first()
    return render_template('dashboard.html', metrics=metrics)

# --- API: Log Time ---
@app.route('/api/log_time', methods=['POST'])
def api_log_time():
    data = request.get_json() or {}
    minutes = data.get('minutes')
    if not isinstance(minutes, int):
        return jsonify({'success': False, 'error': 'Minutes must be an integer.'}), 400
    metrics = Metric.query.first()
    # Allow both positive (add) and negative (remove) time, but don't allow negative totals
    if minutes > 0:
        metrics.daily_played += minutes
        metrics.weekly_played += minutes
        metrics.monthly_played += minutes
    elif minutes < 0:
        metrics.daily_played = max(0, metrics.daily_played + minutes)
        metrics.weekly_played = max(0, metrics.weekly_played + minutes)
        metrics.monthly_played = max(0, metrics.monthly_played + minutes)
    else:
        return jsonify({'success': False, 'error': 'Minutes must not be zero.'}), 400
    # Enforce coherence: monthly >= weekly >= daily
    metrics.weekly_played = max(metrics.weekly_played, metrics.daily_played)
    metrics.monthly_played = max(metrics.monthly_played, metrics.weekly_played)
    db.session.commit()
    return jsonify({'success': True, 'daily_played': metrics.daily_played, 'weekly_played': metrics.weekly_played, 'monthly_played': metrics.monthly_played,
                    'daily_goal': metrics.daily_goal, 'weekly_goal': metrics.weekly_goal, 'monthly_goal': metrics.monthly_goal})

# --- API: Reset Metric ---
@app.route('/api/reset_metric', methods=['POST'])
def api_reset_metric():
    data = request.get_json() or {}
    metric_type = data.get('type', 'daily')
    metrics = Metric.query.first()
    if metric_type == 'daily':
        metrics.daily_played = 0
    elif metric_type == 'weekly':
        metrics.weekly_played = 0
    elif metric_type == 'monthly':
        metrics.monthly_played = 0
    elif metric_type == 'all':
        metrics.daily_played = 0
        metrics.weekly_played = 0
        metrics.monthly_played = 0
    else:
        return jsonify({'success': False, 'error': 'Invalid metric type.'}), 400
    db.session.commit()
    return jsonify({'success': True})

# --- API: Get Metrics (for reload) ---
@app.route('/api/metrics')
def api_metrics():
    metrics = Metric.query.first()
    if not metrics:
        return jsonify({'success': False, 'error': 'No metrics found.'}), 404
    return jsonify({
        'weekly_goal': metrics.weekly_goal,
        'daily_goal': metrics.daily_goal,
        'monthly_goal': metrics.monthly_goal,
        'weekly_played': metrics.weekly_played,
        'daily_played': metrics.daily_played,
        'monthly_played': metrics.monthly_played,
        'high_score': metrics.high_score
    })

# --- API: Reset DB to Demo State ---
@app.route('/api/reset_demo', methods=['POST'])
def reset_demo():
    db_path = os.path.join('instance', 'respectcircle.db')
    sql_path = 'init_demo.sql'
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
        subprocess.run(f'sqlite3 {db_path} < {sql_path}', shell=True, check=True)
        logger.info('Database reset to demo state.')
        # Dispose SQLAlchemy session and engine to avoid stale connections
        db.session.remove()
        db.engine.dispose()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    return jsonify({'success': True})

@app.route('/api/set_played', methods=['POST'])
def set_played():
    data = request.get_json() or {}
    metrics = Metric.query.first()
    daily = data.get('daily_played', metrics.daily_played)
    weekly = data.get('weekly_played', metrics.weekly_played)
    monthly = data.get('monthly_played', metrics.monthly_played)
    # Enforce coherence: monthly >= weekly >= daily
    try:
        daily = int(daily)
        weekly = int(weekly)
        monthly = int(monthly)
    except Exception:
        return jsonify({'success': False, 'error': 'All values must be integers.'}), 400
    if not (0 <= daily <= weekly <= monthly):
        return jsonify({'success': False, 'error': 'Must have monthly >= weekly >= daily >= 0.'}), 400
    metrics.daily_played = daily
    metrics.weekly_played = weekly
    metrics.monthly_played = monthly
    db.session.commit()
    return jsonify({'success': True, 'daily_played': metrics.daily_played, 'weekly_played': metrics.weekly_played, 'monthly_played': metrics.monthly_played})

@app.route('/set_played_demo', methods=['GET', 'POST'])
def set_played_demo():
    msg = None
    if request.method == 'POST':
        try:
            daily = int(request.form.get('daily_played', 0))
            weekly = int(request.form.get('weekly_played', 0))
            monthly = int(request.form.get('monthly_played', 0))
            if not (0 <= daily <= weekly <= monthly):
                msg = 'Error: Must have monthly ≥ weekly ≥ daily ≥ 0.'
            else:
                metrics = Metric.query.first()
                metrics.daily_played = daily
                metrics.weekly_played = weekly
                metrics.monthly_played = monthly
                db.session.commit()
                msg = 'Values updated!'
        except Exception as e:
            msg = f'Error: {e}'
    return render_template('set_played_demo.html', msg=msg)

# --- API: Set Goals ---
@app.route('/api/set_goals', methods=['POST'])
def set_goals():
    data = request.get_json() or {}
    metrics = Metric.query.first()
    try:
        daily = int(data.get('daily_goal', metrics.daily_goal))
        weekly = int(data.get('weekly_goal', metrics.weekly_goal))
        monthly = int(data.get('monthly_goal', metrics.monthly_goal))
    except Exception:
        return jsonify({'success': False, 'error': 'All values must be integers.'}), 400
    if not (0 < daily <= weekly <= monthly):
        return jsonify({'success': False, 'error': 'Must have monthly ≥ weekly ≥ daily > 0.'}), 400
    metrics.daily_goal = daily
    metrics.weekly_goal = weekly
    metrics.monthly_goal = monthly
    db.session.commit()
    return jsonify({'success': True, 'daily_goal': metrics.daily_goal, 'weekly_goal': metrics.weekly_goal, 'monthly_goal': metrics.monthly_goal})
