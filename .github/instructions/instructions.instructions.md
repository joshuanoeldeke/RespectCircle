# RespectCircle Coding Standards & Workflow

## Overview
RespectCircle is a Flask web app designed for accessibility, maintainability, and extensibility. All code should be modular, readable, and ready for future features (e.g., authentication, blueprints).

## Workflow
- Use feature branches and pull requests for all changes
- Write clear, concise commit messages
- Test all changes locally before merging
- Ensure all UI changes are accessible (see below)

## Coding Standards
- **Python**: Follow PEP8, use type hints where possible, modularize logic (models, routes, API), and always filter data by user for multi-user support
- **HTML**: Use semantic HTML5, ARIA roles/labels, and Bootstrap 5 best practices
- **CSS**: Use variables, ensure high-contrast, and provide visible focus states
- **JS**: Modularize scripts, log key actions, and ensure all dynamic content is accessible
- **Templates**: Use Jinja2 blocks, extend `base.html`, and avoid duplication. Always provide user context for personalized dashboards.

## Accessibility
- All forms and buttons must have ARIA labels and visible focus states
- Modal dialogs and navigation must be keyboard and screen reader accessible
- Color choices must meet WCAG AA contrast
- Large, clear fonts and touch targets

## Extensibility
- Organize code for easy addition of blueprints, authentication, and new features (multi-user support is required)
- Keep API endpoints concise and well-logged
- Use Jinja2 blocks for template extensibility

## Navigation & Pages
- **Dashboard**: `/dashboard` — Activity rings, log/reset time, feed, and edit goals (modal)
- **Settings**: `/settings` — User selection/creation/deletion
- Navigation links must be present in the navbar for both pages.

## Next Steps & Suggestions
- Add Flask blueprints for modularity
- Implement authentication (Flask-Login)
- Add automated accessibility and unit tests
- Expand API for mobile or third-party integration

## Questions?
Open an issue or contact the maintainer.