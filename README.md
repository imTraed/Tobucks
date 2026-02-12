# Tobucks – Next-Gen Movie Recommendation System

> **⚠️ LEGAL NOTICE: PRIVATE PROPERTY**
>
> **Copyright (c) 2026 Joshua Jacome. All rights reserved.**
> 
> This software and its source code are the exclusive intellectual property of the author. Copying, distribution, modification, or use without written authorization is strictly prohibited. This repository is published solely for **academic evaluation purposes**.

---

Tobucks is an advanced web application built with Flask that transforms how users discover cinema. Beyond simple filtering, Tobucks uses Artificial Intelligence to understand user narratives and automatically build its own movie catalog in real-time.

## 🚀 Key Features

- **AI Concierge Experience**: Powered by Groq (Llama 3), users can describe what they want to watch in natural language. The system understands the "vibe" and era to provide intelligent suggestions.
- **Self-Growing Database (Magic Import)**: If a recommended movie isn't in the local database, the system automatically fetches high-quality metadata from OMDb, including posters and ratings.
- **Smart Automation**:
    - **Auto-Translation**: English synopses are instantly translated to Spanish.
    - **Auto-Trailer Discovery**: Searches and embeds YouTube trailers automatically for every new entry.
    - **Genre Normalization**: Dynamically creates and translates genres to maintain a clean, Spanish-language catalog.
- **Multi-Platform Optimization**: A fully responsive interface with dedicated **Web and Mobile** versions, ensuring a premium experience on any device.
- **Interactive Graph Visualization**: Uses D3.js to show the complex connections between genres and the movie library.
- **Robust Security**: Complete user authentication system with session management and administrative controls.

## 📱 Interface Preview
- **Desktop version**
<img width="1884" height="885" alt="Tobucks Desktop Interface" src="https://github.com/user-attachments/assets/effa5d41-3f5e-48a1-919f-e3217387cd45" />
- **Mobile version**:
- <img width="1179" height="2128" alt="IMG_2558" src="https://github.com/user-attachments/assets/329d5ad7-58a8-428c-86d5-2e19f8705c14" />
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
