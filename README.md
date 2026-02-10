# Tobucks – Movie Recommendation System

> **⚠️ LEGAL NOTICE: PRIVATE PROPERTY**
>
> **Copyright (c) 2026 Joshua Jacome. All rights reserved.**
>
> This software and its source code are the exclusive intellectual property of the author.
> Copying, distribution, modification, or use without written authorization is strictly prohibited.
> This repository is published solely for **academic evaluation purposes**.

---

Tobucks is a web application built with Flask that allows users to receive movie recommendations based on their favorite genres. Administrators can manage the movie catalog and available genres, while registered users can indicate their preferences and receive personalized suggestions.

## Features

- **Modular Architecture**: The code is organized into blueprints to separate the logic for movies, genres, users, and recommendations.
- **Persistence with SQLAlchemy**: It uses a relational database (default MySQL) and defines tables for movies, genres, and user preferences.
- **CRUD Operations**: Includes forms to create, list, update, and delete movies and genres.
- **User Authentication**: Users can register, log in, and log out. Only authenticated users can access protected areas.
- **Preferences and Recommendations**: Users select their preferred genres, and the system calculates recommendations based on genre matching.
- **Graph Visualization**: An interactive graph shows how genres and movies are connected using D3.js.
- **Responsive Design**: Bootstrap is used to ensure a modern and adaptable interface for various screen sizes.

<img width="1884" height="885" alt="{AC9DF461-BC5D-469D-A565-4B8933247C1C}" src="https://github.com/user-attachments/assets/effa5d41-3f5e-48a1-919f-e3217387cd45" />

## Installation and Execution (For Evaluation Only)

1. **Clone or copy the repository** into your working environment.

2. **Create a Python virtual environment and install dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure the database:**
   Modify the `DATABASE_URI` variable in `tobucks/config.py` or export the `DATABASE_URI` environment variable with the connection string to your MySQL server. You can also use SQLite during development:

   ```bash
   export DATABASE_URI=sqlite:///tobucks.db
   # On Windows (PowerShell): $env:DATABASE_URI="sqlite:///tobucks.db"
   ```

4. **Initialize the tables:**
   After configuring the database, run the migrations (requires `Flask-Migrate`). From the project’s root directory:

   ```bash
   flask db init
   flask db migrate -m "Initial creation"
   flask db upgrade
   ```

5. **Start the server:**

   ```bash
   python run.py
   ```

   Visit `http://localhost:5000` in your browser.

## Notes

- The project requires MySQL to be installed and accessible if using the default driver. The `pymysql` dependency is included in `requirements.txt` to connect to MySQL.

<img width="1832" height="886" alt="{F9EC3C9C-E4FD-44B8-8402-755793C83982}" src="https://github.com/user-attachments/assets/13ccfe41-e23e-44a2-8f99-623b00268627" />

- For demonstration purposes in an environment without MySQL, you can use SQLite by configuring the `DATABASE_URI` variable as `sqlite:///tobucks.db`.

<img width="1863" height="861" alt="{A2CB2919-276D-4D38-891B-88EA7ECB6273}" src="https://github.com/user-attachments/assets/b153f218-9742-431f-b006-613609d97503" />

- The graph visualization is based on D3.js loaded from a CDN. Ensure you have internet access when running the application if you wish to view the interactive graph.

<img width="1864" height="888" alt="{EBCA45C4-FAA9-47CF-BEC3-88D8AA49B2A8}" src="https://github.com/user-attachments/assets/9d3b7f6e-150c-4ee9-9360-bf083d7ac017" />

## Author

**Joshua Jacome**

* **Project Status:** Private / Academic Evaluation
* **Copyright:** © 2026 Joshua Jacome. All Rights Reserved.