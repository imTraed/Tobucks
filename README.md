# Tobucks – Next-Gen Movie Recommendation System

> **⚠️ LEGAL NOTICE: PRIVATE PROPERTY**
>
> **Copyright (c) 2026 Joshua Jacome. All rights reserved.**
> 
> This software and its source code are the exclusive intellectual property of the author. Copying, distribution, modification, or use without written authorization is strictly prohibited. This repository is published solely for **academic evaluation purposes**.

---

Tobucks is an advanced web application built with Flask that transforms how users discover cinema. Beyond simple filtering, Tobucks uses Artificial Intelligence to understand user narratives and automatically build its own movie catalog in real-time.

## 🚀 Key Features

- **AI Concierge Experience**: Powered by Groq (Llama 3.3), users can describe what they want to watch in natural language. The system entiende el "vibe" y la época para dar sugerencias inteligentes.
- **Self-Growing Database (Magic Import)**: Si una película no está en la base de datos local, el sistema obtiene automáticamente metadatos de OMDb, incluyendo pósters y calificaciones.
- **Smart Automation**:
    - **Auto-Translation**: Las sinopsis en inglés se traducen instantáneamente al español.
    - **Auto-Trailer Discovery**: Busca e integra trailers de YouTube automáticamente.
    - **Genre Normalization**: Traduce y crea géneros dinámicamente para mantener el catálogo limpio.
- **Multi-Platform Optimization**: Interfaz responsiva con versiones dedicadas para **Web y Mobile**.
- **Interactive Graph Visualization**: Usa D3.js para mostrar las conexiones entre géneros y películas.
- **Robust Security**: Sistema de autenticación completo con gestión de sesiones y roles administrativos.

## 📱 Interface Preview

<table width="100%">
  <tr>
    <td width="60%" align="center" valign="top">
      <strong>🖥️ Desktop Version</strong><br>
      <img src="https://github.com/user-attachments/assets/effa5d41-3f5e-48a1-919f-e3217387cd45" alt="Tobucks Desktop Interface" style="border-radius: 10px; margin-top: 10px;">
    </td>
    <td width="40%" align="center" valign="top">
      <strong>📱 Mobile Version</strong><br>
      <img src="https://github.com/user-attachments/assets/329d5ad7-58a8-428c-86d5-2e19f8705c14" alt="Tobucks Mobile Interface" style="border-radius: 10px; margin-top: 10px;">
    </td>
  </tr>
</table>

*The system adapts seamlessly between high-resolution desktop monitors and mobile touchscreens.*

## 🛠️ Tech Stack

- **Backend**: Python 3.x / Flask
- **AI/LLM**: Groq Cloud API (Llama 3.3)
- **Database**: SQLAlchemy (Support for SQLite & PostgreSQL)
- **Frontend**: Bootstrap 5, Jinja2, D3.js
- **APIs**: OMDb API, YouTube Search Python, Google Translate API

## ⚙️ Installation and Execution

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
Crea un archivo .env en la raíz y añade tus llaves:

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
Visita http://localhost:5000 para iniciar la experiencia.

📝 Technical Notes
Responsive Design: La UI incluye media queries específicas para navegación móvil y botones táctiles.

Dynamic Catalog: Diseñado para crecer orgánicamente basado en la interacción del usuario.

Data Persistence: Arquitectura modular con Blueprints para separar la lógica de negocio de los servicios de IA.

👨‍💻 Author
Joshua Jacome Engineering in Systems Student

Project Status: Private / Academic Evaluation