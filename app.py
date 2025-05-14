from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import date

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # needed for flash messages

# In-memory data
metrics = {
    "weekly_goal": 300,   # minutes per week
    "daily_goal": 60,    # minutes per day
    "weekly_played": 120, # sample data
    "high_score": 8500    # sample score
}
goals = [
    {"id": 1, "title": "10-min daily walk", "target": 70, "progress": 40},
    {"id": 2, "title": "Tai Chi session",     "target": 30, "progress": 10},
]
feed = [
    {"by": "Lisa", "text": "Dad scored 8500 points today!", "time": "2h ago"},
    {"by": "Chen", "text": "Grandma completed her first week!", "time": "1d ago"},
]

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    pct = int(metrics["weekly_played"] / metrics["weekly_goal"] * 100)
    return render_template('dashboard.html',
                           weekly_goal=metrics["weekly_goal"],
                           weekly_played=metrics["weekly_played"],
                           pct_played=pct,
                           high_score=metrics["high_score"])

@app.route('/goals', methods=['GET', 'POST'])
def manage_goals():
    errors = {}
    form_data = {}
    if request.method == 'POST':
        # collect and validate inputs
        title = request.form.get('title','').strip()
        target_raw = request.form.get('target','').strip()
        form_data['title'] = title
        form_data['target'] = target_raw
        if not title:
            errors['title'] = 'Please enter a goal title.'
        try:
            target = int(target_raw)
            if target <= 0:
                errors['target'] = 'Target minutes must be positive.'
        except ValueError:
            errors['target'] = 'Please enter a valid number.'
        if errors:
            flash('Please fix the errors below.', 'danger')
            return render_template('goals.html', goals=goals, errors=errors, form_data=form_data)
        # create goal
        new_id = max(g["id"] for g in goals) + 1 if goals else 1
        goals.append({"id": new_id, "title": title, "target": target, "progress": 0})
        flash('Goal added successfully!', 'success')
        return redirect(url_for('manage_goals'))
    # GET
    return render_template('goals.html', goals=goals, errors={}, form_data={})

@app.route('/goals/update/<int:goal_id>', methods=['POST'])
def update_goal(goal_id):
    amt = int(request.form['progress'])
    for g in goals:
        if g["id"] == goal_id:
            g["progress"] = min(g["target"], g["progress"] + amt)
            break
    flash('Progress updated!', 'success')
    return redirect(url_for('manage_goals'))

@app.route('/feed', methods=['GET', 'POST'])
def show_feed():
    errors = {}
    form_data = {}
    if request.method == 'POST':
        # collect and validate inputs
        by = request.form.get('by','').strip()
        text = request.form.get('text','').strip()
        form_data['by'] = by
        form_data['text'] = text
        if not by:
            errors['by'] = 'Please enter your name.'
        if not text:
            errors['text'] = 'Please enter a moment.'
        if errors:
            flash('Please fix the errors below.', 'danger')
            return render_template('feed.html', feed=feed, errors=errors, form_data=form_data)
        # add to feed
        feed.insert(0, {"by": by, "text": text, "time": "just now"})
        flash('Respect moment posted!', 'success')
        return redirect(url_for('show_feed'))
    # GET
    return render_template('feed.html', feed=feed, errors={}, form_data={})

@app.route('/api/feed', methods=['POST'])
def api_feed():
    data = request.get_json() or {}
    by = data.get('by','').strip()
    text = data.get('text','').strip()
    if not by or not text:
        return jsonify({'error':'Name and moment are required.'}), 400
    entry = {'by': by, 'text': text, 'time': 'just now'}
    feed.insert(0, entry)
    return jsonify(entry)

@app.route('/api/goals', methods=['POST'])
def api_goals():
    data = request.get_json() or {}
    title = data.get('title','').strip()
    target = data.get('target')
    if not title or not isinstance(target, int) or target <= 0:
        return jsonify({'error':'Title and positive target required.'}), 400
    new_id = max((g['id'] for g in goals), default=0) + 1
    goal = {'id': new_id, 'title': title, 'target': target, 'progress': 0}
    goals.append(goal)
    return jsonify(goal)

@app.route('/api/goals/update/<int:goal_id>', methods=['POST'])
def api_update_goal(goal_id):
    data = request.get_json() or {}
    amt = data.get('progress')
    try:
        amt = int(amt)
    except (TypeError, ValueError):
        return jsonify({'error':'Invalid progress value.'}), 400
    for g in goals:
        if g['id'] == goal_id:
            g['progress'] = min(g['target'], g['progress'] + amt)
            return jsonify(g)
    return jsonify({'error':'Goal not found.'}), 404

@app.route('/api/metrics')
def api_metrics():
    pct = int(metrics['weekly_played'] / metrics['weekly_goal'] * 100)
    data = metrics.copy()
    data['pct_played'] = pct
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
