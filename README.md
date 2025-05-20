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

## License
MIT