# Time Tracking & Analytics Dashboard

Harvard's CS50x: Introduction to Computer Science - Final Project


## Overview

OptiTrack is a web-based time tracking application designed to help users understand how they spend their time across different life areas.
Users can log activities in predefined categories and subcategories, track sessions over time, and visualize their data through an interactive dashboard.

The goal of the project is to combine:

- Backend logic (Flask + SQLite)
- Data modeling and transformations
- A clean, user-friendly UI
- Analytical dashboards with meaningful KPIs

## Main Features
- User authentication (register, login, logout)
- Secure password hashing
- Activity tracking with categories and subcategories
- Daily and weekly dashboard views + history
- Interactive dashboard:
    - Daily and weekly views
    - Category selection 
    - KPI cards with progress indicators
    - Time by category
    - Subcategory breakdown
    - Category share
    - Weekly trend per category
- Responsive design (mobile & desktop)

## Architecture Overview
### Application Layer (Flask)
- User authentication & sessions
- Activity selection & tracking (start / stop sessions)
- Dashboard rendering
- Lightweight frontend logic (Jinja + JS)

### Transactional Data Layer (SQLite tables)
This layer captures raw, append-only facts, similar to an OLTP system.

- `users` — user accounts & setup state
- `user_activities` — allowed categories & subcategories per user
- `events` — raw time-tracking events

## Data Modelling
The analytics logic is intentionally separated from the app logic and implemented in SQL.

### Staging/Facts Layer
- `vw_events_facts_daily` - A cleaned view built from raw events used to display sessions history. Single source of truth for analytics.
- `vw_events_facts_daily_split` - A cleaned view built from raw events to be further aggregated.
  
Both views filter completed sessions, calculate duration in seconds, and derive date and weekday attributes.

### Analytics Layer
- `vw_daily_activity` - Built on top of `vw_events_facts_split` using aggregations.

## Technologies Used
- **Backend:** Python, Flask
- **Database:** SQLite
- **Analytics:** SQL views, pandas
- **Frontend:** HTML/CSS, Jinja, Bootstrap, JS, plotly
- **Auth:** Session-based authentication


## How to Run the Application
1. Install dependencies
```
pip install -r requirements.txt
```

3. Initialize the database
```
sqlite3 app.db < schema.sql
```

4. Run the application
```
flask run
```
 
6. Then open your browser and navigate to:
```
http://127.0.0.1:5000
```


## Future Improvements
- Migrate SQLite to PostgreSQL
- Add a dbt-style model structure
- Add features:
    - Edit and delete sessions
    - Export data (CSV)
    - User-defined categories
    - Dark mode
- Expand analytics:
    - Monthly and yearly views
    - Dashboard customization

<!-- 
## Authentication Notes
- Passwords are hashed using Werkzeug security utilities.
- The application uses Flask sessions for login state management.
-->

