# Copilot Instructions

This project is a Python web app called "RespectCircle." Its goal is to help families and friends support and celebrate the progress of elderly users using a game-like rehab device (e.g., a racing wheel for seniors). The app is inspired by Apple Watch's activity rings, focusing on motivation, social support, and daily/weekly goal tracking.

## General Guidelines

- Prioritize accessibility and simplicity in UI: large buttons, clear fonts, and easy navigation.
- The main users are elderly people and their family/caregivers. Family members can set goals, view progress (time played, high scores), and post encouragement.
- Use Flask for the backend and Bootstrap or similar for responsive, accessible frontend.
- Track and visualize metrics like "minutes played" and "high score" as progress rings or bars.
- Allow family/friends to post "Respect Moments" (short messages) to a social feed.
- Make it easy to add, update, and display goals and progress.
- All code should be clear, well-commented, and use Python best practices.

## Coding Standards

- Use snake_case for Python variables and functions.
- Use Jinja2 templates for rendering HTML pages.
- Use Bootstrap classes for responsive layouts.
- Write docstrings for all functions and classes.
- Keep code modular and readable.

## Project Requirements

- Prioritize features that encourage family participation and positive feedback.
- All forms and displays should be accessible for elderly users (large text, high contrast).
- The app should be easy to run locally for prototyping (no database required; use in-memory storage).
- Suggestions for improvements or new features should align with the goal of redefining societal respect for elders in Asia.

## Next Improvements
- **Data Persistence**: Introduce a lightweight database (SQLite) or file-based storage instead of in-memory lists so data survives restarts. ✅
- **Visual Progress Rings**: Replace progress bars with circular progress indicators (e.g., using Chart.js or D3) for more motivational visuals. ✅
- **Authentication & User Roles**: Add login for family members and caregivers; restrict goal creation/updating to authorized users, and allow elders to view but not modify.
- **Real-time Notifications & Alerts**: Integrate WebSockets or server-sent events for live updates, including confetti celebrations on goal completion.
- **Accessibility Enhancements**: Support larger font sizes, high-contrast mode, keyboard navigation, and ARIA labels to meet WCAG standards.
- **Unit & Integration Tests**: Add pytest tests for API endpoints, form validations, and template rendering to ensure reliability.
- **Internationalization**: Prepare templates and messages for multiple languages (e.g., English, Japanese, Chinese) to broaden adoption.
- **Deployment & CI/CD**: Configure GitHub Actions for automated testing and linting, and Dockerize the app for consistent local/production environments.
- **Responsive Design Audit**: Test and tweak the layout on various device sizes (tablets, mobile) and optimize touch targets for elderly users.