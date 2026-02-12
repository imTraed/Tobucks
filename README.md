# Tobucks – Next-Gen Movie Recommendation System

> **⚠️ LEGAL NOTICE: PRIVATE PROPERTY**
>
> **Copyright (c) 2026 Joshua Jacome. All rights reserved.**
> 
> This software and its source code are the exclusive intellectual property of the author. Copying, distribution, modification, or use without written authorization is strictly prohibited. This repository is published solely for **academic evaluation purposes**.

---

Tobucks is an advanced web application built with Flask that transforms how users discover cinema. Beyond simple filtering, Tobucks uses Artificial Intelligence to understand user narratives and automatically build its own movie catalog in real-time.

## 🚀 Key Features

- **AI Concierge Experience**: Powered by Groq (Llama 3), users can describe what they want to watch in natural language. The system entiende la "vibra" y la época para ofrecer sugerencias inteligentes.
- **Self-Growing Database (Magic Import)**: Si una película recomendada no está en la base de datos local, el sistema obtiene automáticamente metadatos de alta calidad de OMDb, incluyendo pósters y calificaciones.
- **Smart Automation**:
    - **Auto-Translation**: Las sinopsis en inglés se traducen instantáneamente al español.
    - **Auto-Trailer Discovery**: Busca y vincula trailers de YouTube automáticamente para cada nueva entrada.
    - **Genre Normalization**: Crea y traduce géneros dinámicamente para mantener un catálogo limpio en español.
- **Multi-Platform Optimization**: Interfaz totalmente responsiva con versiones optimizadas para **PC y Móvil**, garantizando una experiencia premium en cualquier dispositivo.
- **Interactive Graph Visualization**: Utiliza D3.js para mostrar las conexiones complejas entre géneros y la biblioteca de películas.
- **Robust Security**: Sistema completo de autenticación de usuarios con gestión de sesiones y controles administrativos.

## 📱 Interface Preview

| **Desktop Version** | **Mobile Version** |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/effa5d41-3f5e-48a1-919f-e3217387cd45" width="100%" alt="Tobucks Desktop" /> | <img src="https://github.com/user-attachments/assets/329d5ad7-58a8-428c-86d5-2e19f8705c14" width="220" alt="Tobucks Mobile" /> |

*El sistema se adapta perfectamente entre monitores de escritorio de alta resolución y pantallas táctiles móviles.*

## 🛠️ Tech Stack

- **Backend**: Python 3.x / Flask
- **AI/LLM**: Groq Cloud API (Llama 3.3)
- **Database**: SQLAlchemy (Soporte para SQLite & PostgreSQL)
- **Frontend**: Bootstrap 5, Jinja2, D3.js
- **APIs**: OMDb API, YouTube Search Python, Google Translate API

## ⚙️ Installation and Execution

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/JoshuaJacome/Tobucks.git](https://github.com/JoshuaJacome/Tobucks.git)
   cd Tobucks