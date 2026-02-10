# Script para crear tabla de películas vistas
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Crear tabla intermedia usuario-película vista
    try:
        with db.engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS seen_movies (
                    user_id INTEGER NOT NULL,
                    movie_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, movie_id),
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(movie_id) REFERENCES movies(id)
                )
            """))
            print("✅ Tabla creada.")
    except Exception as e:
        print(f"Error: {e}")