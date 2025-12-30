# Time Tracking & Analytics Dashboard

Harvard's CS50x: Introduction to Computer Science - Final Project


## Overview

OptiTrack is a web-based time tracking application designed to help users understand how they spend their time across different life areas.
Users can log activities in predefined categories and subcategories, track sessions over time, and visualize their data through an interactive dashboard.

The goal of the project is to combine:

- Backend logic (Flask + SQLite)
- Data modeling and transformations
- A clean, user-friendly UI
- Analytical dashboards that turn raw events into insights

## Features
- User authentication (register, login, logout)
- Secure password hashing
- Activity tracking with categories and subcategories
- Daily and weekly dashboard views
- Interactive dashboard:
    - KPI cards with progress indicators
    - Time by category
    - Subcategory breakdown
    - Category share
    - Weekly trend per category
- Responsive design (mobile & desktop)
- Clean, consistent UI styling

## Technologies Used
- Python
- Flask
- SQLite
- Pandas
- Plotly
- HTML / Jinja
- CSS
- Bootstrap 5

## How to Run the Application
1. Install dependencies
```pip install -r requirements.txt```

2. Initialize the database
```sqlite3 app.db < schema.sql```

3. Run the application
```flask run```
 
4. Then open your browser and navigate to:
```http://127.0.0.1:5000```


## Authentication Notes
- Passwords are hashed using Werkzeug security utilities.
- Existing user accounts are not affected by changes to password validation rules.
- The application uses Flask sessions for login state management.

## Dashboard Logic
- Today view shows only the current day.
- Last 7 days view aggregates data across the previous week.
- Charts and KPIs automatically adapt to the selected view and category.
- Category selection affects all charts consistently.
- Weekly trends display all categories with muted lines and highlight the selected one.

## Future Improvements
- Edit and delete sessions
- Monthly and yearly views
- Export data (CSV)
- User-defined categories
- Dark mode


#### Author
Roxanna Rodriguez
CS50 Final Project
2025