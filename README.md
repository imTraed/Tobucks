# Tobucks – Next-Gen Movie Recommendation System

> **LEGAL NOTICE: PRIVATE PROPERTY**
>
> **Copyright (c) 2026 Joshua Jacome. All rights reserved.**
> 
> This software and its source code are the exclusive intellectual property of the author. Copying, distribution, modification, or use without written authorization is strictly prohibited. This repository is published solely for **academic evaluation purposes**.

---

Tobucks is an advanced web application built with Flask that transforms how users discover cinema. Beyond simple filtering, Tobucks uses Artificial Intelligence to understand user narratives and automatically build its own movie catalog in real-time.

## Key Features

<<<<<<< HEAD
- **AI Concierge Experience**: Powered by Groq (Llama 3.3), users can describe what they want to watch in natural language. The system understands the "vibe" and era to provide intelligent suggestions.
- **Self-Growing Database (Magic Import)**: If a recommended movie isn't in the local database, the system automatically fetches high-quality metadata from OMDb, including posters and ratings.
=======
- **AI Concierge Experience**: Powered by Groq (Llama 3), users can describe what they want to watch in natural language. The system entiende la "vibra" y la época para ofrecer sugerencias inteligentes.
- **Self-Growing Database (Magic Import)**: Si una película recomendada no está en la base de datos local, el sistema obtiene automáticamente metadatos de alta calidad de OMDb, incluyendo pósters y calificaciones.
>>>>>>> 6874709 (fix: sincronizando secuencias de IDs para evitar UniqueViolation)
- **Smart Automation**:
    - **Auto-Translation**: Las sinopsis en inglés se traducen instantáneamente al español.
    - **Auto-Trailer Discovery**: Busca y vincula trailers de YouTube automáticamente para cada nueva entrada.
    - **Genre Normalization**: Crea y traduce géneros dinámicamente para mantener un catálogo limpio en español.
- **Multi-Platform Optimization**: Interfaz totalmente responsiva con versiones optimizadas para **PC y Móvil**, garantizando una experiencia premium en cualquier dispositivo.
- **Interactive Graph Visualization**: Utiliza D3.js para mostrar las conexiones complejas entre géneros y la biblioteca de películas.
- **Robust Security**: Sistema completo de autenticación de usuarios con gestión de sesiones y controles administrativos.

<<<<<<< HEAD
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
=======
## 📱 Interface Preview

| **Desktop Version** | **Mobile Version** |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/effa5d41-3f5e-48a1-919f-e3217387cd45" width="100%" alt="Tobucks Desktop" /> | <img src="https://github.com/user-attachments/assets/329d5ad7-58a8-428c-86d5-2e19f8705c14" width="220" alt="Tobucks Mobile" /> |

*El sistema se adapta perfectamente entre monitores de escritorio de alta resolución y pantallas táctiles móviles.*
>>>>>>> 6874709 (fix: sincronizando secuencias de IDs para evitar UniqueViolation)

## Tech Stack

- **Backend**: Python 3.x / Flask
- **AI/LLM**: Groq Cloud API (Llama 3.3)
- **Database**: SQLAlchemy (Soporte para SQLite & PostgreSQL)
- **Frontend**: Bootstrap 5, Jinja2, D3.js
- **APIs**: OMDb API, YouTube Search Python, Google Translate API

## Installation and Execution

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/JoshuaJacome/Tobucks.git](https://github.com/JoshuaJacome/Tobucks.git)
<<<<<<< HEAD
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
=======
   cd Tobucks
>>>>>>> 6874709 (fix: sincronizando secuencias de IDs para evitar UniqueViolation)
