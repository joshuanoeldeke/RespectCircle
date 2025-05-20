# RespectCircle
# -------------
# A web application to support and celebrate the progress of elderly users using a game-like rehab device. Family and friends can set goals, view progress, and post encouragements.

## Overview
RespectCircle is a Python Flask web app designed to motivate and support elderly users in their rehabilitation or daily activity routines. Inspired by Apple Watch's activity rings, it enables families and friends to set goals, track progress, and post encouragements in a social feed.

## Features
- Accessible, simple UI (large buttons, clear fonts, high contrast)
- Track metrics: minutes played, high score, daily/weekly/monthly progress
- Visualize progress with rings/bars (Chart.js or similar)
- Family/friends can post "Respect Moments" to a social feed
- Add/update/display goals and progress
- In-memory or SQLite storage (easy local prototyping)
- Modular, well-documented Python code

## Setup & Usage
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/RespectCircle.git
   cd RespectCircle
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Initialize the database:**
   ```sh
   flask shell < instance/init_demo.sql
   ```
   Or let the app auto-create tables on first run.
4. **Run the app:**
   ```sh
   python app.py
   ```
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Project Structure
- `app.py` — Main Flask app and API endpoints
- `instance/init_demo.sql` — Demo SQLite schema and mock data
- `templates/` — Jinja2 HTML templates
- `static/` — CSS and static assets

## Accessibility & Design
- Large, high-contrast text and buttons
- Responsive layout (Bootstrap)
- Keyboard navigation and ARIA labels (WCAG-ready)

## Next Steps
- Add authentication/user roles
- Real-time notifications (WebSockets/SSE)
- Internationalization (multi-language support)
- Unit/integration tests (pytest)
- Dockerize for deployment

## Contributing
Pull requests and suggestions are welcome! Please align with the mission: redefining societal respect for elders in Asia.

## License
MIT