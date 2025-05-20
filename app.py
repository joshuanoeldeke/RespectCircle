"""
RespectCircle Flask App
----------------------
A web application to support and celebrate the progress of elderly users using a game-like rehab device. Family and friends can set goals, view progress, and post encouragements.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///respectcircle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Metric(db.Model):
    """Tracks play metrics and goals for the user."""
    id = db.Column(db.Integer, primary_key=True)
    weekly_goal = db.Column(db.Integer, default=300)
    daily_goal = db.Column(db.Integer, default=60)
    monthly_goal = db.Column(db.Integer, default=1200)
    weekly_played = db.Column(db.Integer, default=0)
    daily_played = db.Column(db.Integer, default=0)
    monthly_played = db.Column(db.Integer, default=0)
    high_score = db.Column(db.Integer, default=0)

class Goal(db.Model):
    """Represents a user goal with progress tracking."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    target = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.Integer, default=0)

class FeedEntry(db.Model):
    """A short encouragement or achievement message for the feed."""
    id = db.Column(db.Integer, primary_key=True)
    by = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize database and ensure a single Metric row exists
def init_db():
    """Initializes the database and ensures a Metric row exists."""
    with app.app_context():
        db.create_all()
        if not Metric.query.first():
            db.session.add(Metric())
            db.session.commit()

init_db()

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    """Main dashboard: shows metrics, goals, and feed."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            session['username'] = username
            flash('Username updated!', 'success')
        return redirect(url_for('index'))
    metrics = Metric.query.first()
    goals = Goal.query.all()
    feed = FeedEntry.query.order_by(FeedEntry.time.desc()).all()
    return render_template('index.html', metrics=metrics, goals=goals, feed=feed)

# API Endpoints
@app.route('/api/feed', methods=['POST'])
def api_feed():
    """API endpoint to post a new feed entry."""
    data = request.get_json() or {}
    by = data.get('by', '').strip()
    text = data.get('text', '').strip()
    if not by or not text:
        return jsonify({'error': 'Name and message required.'}), 400
    entry = FeedEntry(by=by, text=text)
    db.session.add(entry)
    db.session.commit()
    return jsonify({'success': True, 'entry': {'by': entry.by, 'text': entry.text, 'time': entry.time.strftime('%Y-%m-%d %H:%M')}})

@app.route('/api/goals', methods=['POST'])
def api_goals():
    """API endpoint to add a new goal."""
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    target = data.get('target')
    if not title or not isinstance(target, int) or target <= 0:
        return jsonify({'error': 'Valid title and target required.'}), 400
    goal = Goal(title=title, target=target)
    db.session.add(goal)
    db.session.commit()
    return jsonify({'success': True, 'goal': {'id': goal.id, 'title': goal.title, 'target': goal.target, 'progress': goal.progress}})

@app.route('/api/goals/update/<int:goal_id>', methods=['POST'])
def api_update_goal(goal_id):
    """API endpoint to update progress on a goal."""
    data = request.get_json() or {}
    increment = data.get('increment', 0)
    if not isinstance(increment, int) or increment <= 0:
        return jsonify({'error': 'Increment must be a positive integer.'}), 400
    goal = Goal.query.get_or_404(goal_id)
    goal.progress = min(goal.progress + increment, goal.target)
    db.session.commit()
    return jsonify({'success': True, 'progress': goal.progress})

@app.route('/api/metrics')
def api_metrics():
    """API endpoint to get current metrics."""
    metrics = Metric.query.first()
    if not metrics:
        return jsonify({'error': 'Metrics not found.'}), 404
    return jsonify({
        'weekly_goal': metrics.weekly_goal,
        'daily_goal': metrics.daily_goal,
        'monthly_goal': metrics.monthly_goal,
        'weekly_played': metrics.weekly_played,
        'daily_played': metrics.daily_played,
        'monthly_played': metrics.monthly_played,
        'high_score': metrics.high_score
    })

@app.route('/api/log_time', methods=['POST'])
def api_log_time():
    """API endpoint to log play time and update metrics. Adds a Respect Moment if a goal is achieved."""
    data = request.get_json() or {}
    minutes = data.get('minutes', 0)
    if not isinstance(minutes, int) or minutes <= 0:
        return jsonify({'error': 'Minutes must be a positive integer.'}), 400
    metrics = Metric.query.first()
    if not metrics:
        return jsonify({'error': 'Metrics not found.'}), 404
    # Track previous state for achievement detection
    prev_daily = metrics.daily_played
    prev_weekly = metrics.weekly_played
    prev_monthly = metrics.monthly_played
    metrics.daily_played += minutes
    metrics.weekly_played += minutes
    metrics.monthly_played += minutes
    db.session.commit()
    # Check for achievement and add Respect Moment
    achieved = []
    if prev_daily < metrics.daily_goal <= metrics.daily_played:
        achieved.append('Daily')
    if prev_weekly < metrics.weekly_goal <= metrics.weekly_played:
        achieved.append('Weekly')
    if prev_monthly < metrics.monthly_goal <= metrics.monthly_played:
        achieved.append('Monthly')
    if achieved:
        username = session.get('username', 'Anonymous')
        for goal_type in achieved:
            text = f"{username} achieved their {goal_type.lower()} goal! 🎉"
            entry = FeedEntry(by=username, text=text)
            db.session.add(entry)
        db.session.commit()
    return jsonify({
        'success': True,
        'daily_played': metrics.daily_played,
        'daily_goal': metrics.daily_goal,
        'weekly_played': metrics.weekly_played,
        'weekly_goal': metrics.weekly_goal,
        'monthly_played': metrics.monthly_played,
        'monthly_goal': metrics.monthly_goal
    })

@app.route('/api/reset_metric', methods=['POST'])
def api_reset_metric():
    """API endpoint to reset a metric (daily, weekly, or monthly) played value to 0."""
    data = request.get_json() or {}
    metric_type = data.get('type')
    metrics = Metric.query.first()
    if not metrics or metric_type not in ['daily', 'weekly', 'monthly']:
        return jsonify({'error': 'Invalid metric type.'}), 400
    if metric_type == 'daily':
        metrics.daily_played = 0
    elif metric_type == 'weekly':
        metrics.weekly_played = 0
    elif metric_type == 'monthly':
        metrics.monthly_played = 0
    db.session.commit()
    return jsonify({'success': True})

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)