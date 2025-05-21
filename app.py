"""
RespectCircle Flask App (Single User, Single Page)
--------------------------------------------------
A web application to visualize and edit activity goals and progress using animated rings.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import logging
import os, subprocess
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# --- App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///respectcircle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Set session timeout

db = SQLAlchemy(app)

# Initialize Flask-Login and Flask-Bcrypt
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

# Configure the login view for Flask-Login
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- User Model ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Model ---
class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('metrics', lazy=True))
    weekly_goal = db.Column(db.Integer, default=300, nullable=False)
    daily_goal = db.Column(db.Integer, default=60, nullable=False)
    monthly_goal = db.Column(db.Integer, default=1200, nullable=False)
    weekly_played = db.Column(db.Integer, default=0, nullable=False)
    daily_played = db.Column(db.Integer, default=0, nullable=False)
    monthly_played = db.Column(db.Integer, default=0, nullable=False)
    high_score = db.Column(db.Integer, default=0, nullable=False)

# --- DB Initialization ---
init_done = False

# Ensure `init_db` creates all tables and adds a default user
@app.before_request
def init_db():
    global init_done
    if not init_done:
        with app.app_context():
            db.create_all()  # Create all tables
            if not User.query.first():
                user = User(username='default_user')
                user.set_password('password')
                db.session.add(user)
                db.session.commit()
                db.session.add(Metric(user_id=user.id))
                db.session.commit()
        init_done = True

# Replace @app.before_first_request with @app.before_request for session clearing
session_cleared = False

@app.before_request
def clear_session_on_startup():
    global session_cleared
    if not session_cleared:
        session.clear()
        logger.info("Session cache cleared on app startup.")
        session_cleared = True

# --- User Registration ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# --- User Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logger.info(f"Attempting login for username: {username}")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            logger.info(f"Login successful for username: {username}")
            flash('Login successful.')
            return redirect(url_for('dashboard'))
        logger.warning(f"Login failed for username: {username}")
        flash('Invalid username or password.')
    return render_template('login.html')

# --- User Logout ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# --- Main Page ---
@app.route('/', methods=['GET'])
@login_required
def dashboard():
    metrics = Metric.query.filter_by(user_id=current_user.id).first()
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
    project_root = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the project root
    db_path = os.path.join(project_root, 'instance', 'respectcircle.db')
    sql_path = os.path.join(project_root, 'init_demo.sql')  # Use absolute path
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
        subprocess.run(f'sqlite3 {db_path} < {sql_path}', shell=True, check=True)
        logger.info('Database reset to demo state.')
        # Dispose SQLAlchemy session and engine to avoid stale connections
        db.session.remove()
        db.engine.dispose()
        # Clear session and reinitialize database schema
        session.clear()
        with app.app_context():
            db.create_all()
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
