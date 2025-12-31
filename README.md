# OptiTrack: Time Tracking & Analytics Dashboard

*Harvard's CS50x: Introduction to Computer Science - Final Project*


## Overview

OptiTrack is a web-based time tracking application designed to help users understand how they spend their time across different life areas.
Users can log activities in predefined categories and subcategories, track sessions over time, and visualize their data through an interactive dashboard.

The goal of the project is to combine the following aspects:

- Backend logic (Flask + SQLite)
- Data modeling and transformations
- Separation between transactional data and analytics logic
- Analytical dashboard / KPI-driven reporting
- User-friendly UI

Beyond basic time tracking, the core goal of this project is to model, transform, and analyze time-based event data, applying concepts commonly used in data analytics and analytics engineering.

## Project Structure
- `app.py`<br>
Main Flask application. Handles routing, authentication, session logic, and dashboard data loading.

- `helpers.py`<br>
Reusable utility and support functions (login, formatting, database connection).

- `config.py`<br>
Predefined categories/subcategories configuration and name mapping.

- `charts.py`<br>
Chart-building logic (Plotly figures, themes and prep)

- `schema.sql`<br>
Defines database tables and relationships.

- `sql/`<br>
Contains analytics SQL views (staging and analytics layers).

- `templates/`<br>
Jinja templates for rendering pages and dashboard components.

- `static/`<br>
CSS and frontend assets.

## Main Features
- User authentication (register, login, logout)
- Secure password hashing and session-based login
- Activity tracking with categories and subcategories
- Interactive dashboard with:
    - Daily and weekly views
    - Category selection 
    - KPI cards with progress indicators
    - Time by category
    - Subcategory breakdown and share
    - Weekly trend per category
- Responsive design (mobile & desktop)

## Architecture Overview
### Application Layer (Flask)
Responsible for user interaction and control flow:
- Authentication and session management
- Activity setup and validation
- Starting and stopping tracking sessions
- Rendering dashboard views
- Passing filtered data to the frontend

### Transactional Data Layer (SQLite tables)
This layer captures raw, append-only facts, similar to an OLTP system.

- `users` — user accounts & setup state.
- `user_activities` — allowed categories & subcategories per user.
- `events` — raw time-tracking events.

Each row in `events` represents a single tracking session. No analytics or aggregation logic is stored in these tables.

## Data & Analytics Design Decisions
A key design goal of this project was to separate data capture from data analysis. The analytics logic is intentionally separated from the app logic and implemented in SQL.

→ **Events stored "raw"**: sessions are stored exactly as recorded, with no calculations and aggregations. This preserves flexibility and mirrors real-world logging systems.<br>
→ **Analytics lives in SQL**: SQL views are used instead of python transformations. Calculations and aggregations are computed at query time, keeping the python layer thin and focused on application logic. This approach scales naturally to PostgreSQL or a data warehouse.<br>
→ **Views instead of tables**: Views act as reusable, composable data models. Views centralize logic, avoid duplicating data, and make it easy to iterate on the model without backfilling aggregate tables. <br>

### Staging/Facts Layer
- `vw_events_facts_daily` - Cleaned, completed sessions for display/history (duration, date/time fields). Used to render session history pages.
- `vw_events_facts_daily_split` - Canonical facts model for analytics. Produces one row per user/session/day (splits cross-midnight sessions if needed), includes duration in seconds and date attributes. Downstream rollups are built from this.
  
Both views filter completed sessions, calculate duration in seconds, and derive date and weekday attributes.

### Analytics Layer
- `vw_daily_activity` - Daily aggregate built from `vw_events_facts_daily_split`. Serves dashboard KPIs and charts.

This layer aggregates session data by day, category, and subcategory,produces metrics consumed directly by the dashboard and enables daily and weekly rollups without rewriting logic.

Filtering by user and time range happens at query time, allowing the same models to support multiple dashboard views.

## Technologies Used
- **Backend:** Python, Flask
- **Database:** SQLite
- **Analytics:** SQL views, pandas
- **Frontend:** HTML/CSS, Jinja, Bootstrap, JavaScript, Plotly
- **Auth:** Session-based authentication + password hashing


## How to Run the Application
1. Install dependencies
```
pip install -r requirements.txt
```

2. Initialize the database
```
sqlite3 time_management.db < schema.sql
```

3. Run the application
```
flask run
```
 
4. Open your browser and navigate to:
```
http://127.0.0.1:5000
```


## Future Improvements
- Migrate SQLite to PostgreSQL
- Introduce dbt-style model management
- Materialize analytics views for performance
- Add features:
    - Edit and delete sessions
    - Export data (CSV)
    - User-defined categories
    - Setting (password change, preferences, etc)
- Expand analytics:
    - Monthly and yearly views
    - Dashboard customization & goal-setting

<br><br>
> [!NOTE]
> This project was designed not just as a web application, but as a small analytics system. It demonstrates how raw behavioral data can be modeled, transformed, and analyzed using clean data principles — even within a lightweight stack. The analytics layer uses dbt-inspired layered SQL modeling. Models are implemented as views for simplicity; in a production system some would likely be materialized for performance.
<br>

<!-- 
## Authentication Notes
- Passwords are hashed using Werkzeug security utilities.
- The application uses Flask sessions for login state management.
-->

