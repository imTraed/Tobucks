# Tobucks – Next-Gen Movie Recommendation System

> **LEGAL NOTICE: PRIVATE PROPERTY**
>
> **Copyright (c) 2026 Joshua Jacome. All rights reserved.**
> 
> This software and its source code are the exclusive intellectual property of the author. Copying, distribution, modification, or use without written authorization is strictly prohibited. This repository is published solely for **academic evaluation purposes**.

---

Tobucks is an advanced web application built with Flask that transforms how users discover cinema. Beyond simple filtering, Tobucks uses Artificial Intelligence to understand user narratives and automatically build its own movie catalog in real-time.

## Key Features

- **AI Concierge Experience**: Powered by Groq (Llama 3.3), users can describe what they want to watch in natural language. The system understands the "vibe" and era to provide intelligent suggestions.
- **Self-Growing Database (Magic Import)**: If a recommended movie isn't in the local database, the system automatically fetches high-quality metadata from OMDb, including posters and ratings.
- **Smart Automation**:
    - **Auto-Translation**: English synopses are instantly translated to Spanish.
    - **Auto-Trailer Discovery**: Searches and embeds YouTube trailers automatically for every new entry.
    - **Genre Normalization**: Dynamically creates and translates genres to maintain a clean, Spanish-language catalog.
- **Multi-Platform Optimization**: A fully responsive interface with dedicated **Web and Mobile** versions, ensuring a premium experience on any device.
- **Interactive Graph Visualization**: Uses D3.js to show the complex connections between genres and the movie library.
- **Robust Security**: Complete user authentication system with session management and administrative controls.

## Interface Preview

<table width="100%">
  <tr>
    <td width="65%" align="center" valign="top">
      <strong>Desktop Version</strong><br>
      <img src="https://github.com/user-attachments/assets/effa5d41-3f5e-48a1-919f-e3217387cd45" alt="Tobucks Desktop Interface" style="border-radius: 10px; margin-top: 10px;">
    </td>
    <td width="35%" align="center" valign="top">
      <strong>Mobile Version</strong><br>
      <img src="https://github.com/user-attachments/assets/329d5ad7-58a8-428c-86d5-2e19f8705c14" alt="Tobucks Mobile Interface" style="border-radius: 10px; margin-top: 10px;">
    </td>
  </tr>
</table>

*The system adapts seamlessly between high-resolution desktop monitors and mobile touchscreens.*

## Tech Stack

- **Backend**: Python 3.x / Flask
- **AI/LLM**: Groq Cloud API (Llama 3.3)
- **Database**: SQLAlchemy (Support for SQLite & PostgreSQL)
- **Frontend**: Bootstrap 5, Jinja2, D3.js
- **APIs**: OMDb API, YouTube Search Python, Google Translate API

## Installation and Execution

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/JoshuaJacome/Tobucks.git](https://github.com/JoshuaJacome/Tobucks.git)
   cd Tobucks
Create a Virtual Environment and Install Dependencies:

Bash
python -m venv venv
# On Windows
venv\Scripts\activate
# Install Core + AI libraries
python -m pip install -r requirements.txt
Environment Configuration:
Create a .env file in the root directory and add your keys:

Fragmento de código
SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_key
OMDB_API_KEY=your_omdb_key
DATABASE_URL=sqlite:///instance/bus_station.db
Initialize Database:

Bash
flask db upgrade
# Or run the manual creation script
python scripts/create_tables.py
Launch:

Bash
python run.py
Visit http://localhost:5000 to start the experience.

**Technical Notes**
Responsive Design: The UI includes specific CSS media queries to handle mobile navigation bars and touch-friendly action buttons.

Dynamic Catalog: The system is designed to start with an empty database and grow based on user interactions.

Data Persistence: Uses a modular architecture with Blueprints to separate business logic from AI services.

**Author**
Joshua Jacome
Engineering in Systems Student

Project Status: Private / Academic Evaluation

Copyright: © 2026 Joshua Jacome. All Rights Reserved.
