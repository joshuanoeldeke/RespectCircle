# RespectCircle

RespectCircle is a simple, accessible web app for logging and visualizing activity progress using animated rings. Built with Flask and Bootstrap 5, it is designed for ease of use, accessibility, and future extensibility.

## Features
- **Accessible UI**: High-contrast, large touch targets, semantic HTML, ARIA labels, and keyboard navigation.
- **Activity Rings Dashboard**: Visualize daily, weekly, and monthly progress. Log or reset time dynamically.
- **Reset Demo Data**: Restore the app to its initial demo state with one click.
- **Robust Input Validation**: Add/Remove Time only accepts positive integers.
- **Minimal, single-page workflow**: No settings or goal editing UI for maximum reliability.

## Setup
1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app**:
   ```bash
   flask run
   ```
   (To reset demo data, run the SQL in `instance/init_demo.sql` against `instance/respectcircle.db`.)
4. **Visit** [http://localhost:5000](http://localhost:5000)

## Project Structure
- `app.py` — Main Flask app, models, API, and routes (single-user, single-page)
- `templates/` — Jinja2 HTML templates: `dashboard.html`, `base.html`
- `static/css/theme.css` — Custom theme (high-contrast, accessible)
- `requirements.txt` — Only Flask and Flask-SQLAlchemy

## Accessibility
- All forms and buttons have ARIA labels and visible focus states
- Color choices meet WCAG AA contrast
- Large, clear fonts and touch targets

## Extensibility
- Modular codebase: ready for Flask blueprints, authentication, and new features
- All scripts and styles are organized for easy extension
- API endpoints are concise and well-logged

## Running in GitHub Codespaces & API Demo

You can run RespectCircle in [GitHub Codespaces](https://github.com/features/codespaces) for easy cloud-based demos and development.

### 1. Start the App in Codespaces

Open a terminal in your Codespace and run:

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the Flask app on the correct host/port for Codespaces:
python -m flask run --host=0.0.0.0 --port=5000
```

### 2. Make the Port Public

- In the Codespaces UI, click the 'Ports' tab (bottom panel).
- Find port `5000` in the list. Click the globe icon and set it to 'Public'.
- Click the URL to open the app in your browser.

### 3. Using the API Endpoints

You can test the API directly with `curl`, Postman, or the built-in demo form (`Set Rings (Demo)` link on the dashboard).

#### Example: Add 15 minutes
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"minutes": 15}' \
     https://YOUR-CODESPACE-URL/api/log_time
```

#### Example: Remove 10 minutes
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"minutes": -10}' \
     https://YOUR-CODESPACE-URL/api/log_time
```

#### Example: Set ring values directly
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"daily_played": 20, "weekly_played": 50, "monthly_played": 200}' \
     https://YOUR-CODESPACE-URL/api/set_played
```

#### Example: Reset demo data
```bash
curl -X POST https://YOUR-CODESPACE-URL/api/reset_demo
```

- Replace `YOUR-CODESPACE-URL` with the public URL shown in the Ports tab (e.g., `https://5000-yourusername-respectcircle-xxxxxx.github.dev`).
- You can also use Postman or the Set Rings (Demo) form for manual testing.

### Troubleshooting
- If you see a database error, run `./init_db.sh` to initialize/reset the database.
- If the app is not reachable, make sure port 5000 is set to 'Public' in the Ports tab.
- For persistent issues, try stopping and restarting the Codespace.

---

For more details, see the comments in `app.py` and the API documentation above.

## License
MIT