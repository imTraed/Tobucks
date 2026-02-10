# Script para actualizar metadata de películas desde OMDb
import requests
import sqlite3
import os
from app import create_app, db
from app.models.models import Movie

app = create_app()

def get_db_path():
    """Encontrar ruta de base de datos"""
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    if uri.startswith('sqlite:///'):
        filename = uri.replace('sqlite:///', '')
        
        candidates = [
            os.path.join(app.instance_path, filename),
            os.path.join(os.getcwd(), filename),
            os.path.join(os.getcwd(), 'instance', filename),
            os.path.join(os.getcwd(), 'app', filename)
        ]
        
        for path in candidates:
            if os.path.exists(path):
                return path
        
        return candidates[0]
        
    return None

def force_add_columns():
    """Agregar columnas faltantes a la base de datos"""
    db_path = get_db_path()
    print(f"📂 Base de datos: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada.")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar si tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movies';")
        if not cursor.fetchone():
            print("❌ Tabla 'movies' no existe.")
            return False

        # Obtener columnas actuales
        cursor.execute("PRAGMA table_info(movies)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Columnas: {columns}")

        # Agregar rating
        if 'rating' not in columns:
            print("⚠️ Agregando 'rating'...")
            cursor.execute("ALTER TABLE movies ADD COLUMN rating FLOAT DEFAULT 0.0")
            print("✅ Hecho.")
        
        # Agregar runtime
        if 'runtime' not in columns:
            print("⚠️ Agregando 'runtime'...")
            cursor.execute("ALTER TABLE movies ADD COLUMN runtime TEXT")
            print("✅ Hecho.")
            
        conn.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        conn.close()

def update_movies_metadata():
    """Actualizar rating y runtime desde OMDb"""
    omdb_key = app.config.get('OMDB_API_KEY')
    if not omdb_key:
        print("❌ Falta API key")
        return

    with app.app_context():
        print("\n🎬 Actualizando metadata...")
        try:
            movies = Movie.query.all()
        except Exception as e:
            print(f"❌ Error: {e}")
            return

        count = 0
        for movie in movies:
            try:
                # Consultar API
                url = f"http://www.omdbapi.com/?t={movie.title}&apikey={omdb_key}"
                data = requests.get(url).json()

                if data.get('Response') == 'True':
                    # Actualizar rating
                    imdb = data.get('imdbRating', '0')
                    movie.rating = float(imdb) if imdb != 'N/A' else 0.0
                    
                    # Actualizar runtime
                    movie.runtime = data.get('Runtime', 'N/A')
                    
                    print(f"✅ {movie.title[:20]:<20} -> {movie.rating} ⭐")
                    count += 1
                else:
                    print(f"⚠️ No encontrada: {movie.title}")
            except Exception as e:
                print(f"❌ Error: {e}")

        db.session.commit()
        print(f"\n✅ {count} películas actualizadas.")

if __name__ == "__main__":
    if force_add_columns():
        update_movies_metadata()

                if data.get('Response') == 'True':
                    # Rating
                    imdb = data.get('imdbRating', '0')
                    movie.rating = float(imdb) if imdb != 'N/A' else 0.0
                    
                    # Runtime
                    movie.runtime = data.get('Runtime', 'N/A')
                    
                    print(f"✅ {movie.title[:20]:<20} -> {movie.rating} ⭐ | {movie.runtime}")
                    count += 1
                else:
                    print(f"⚠️ No encontrada: {movie.title}")
            except Exception as e:
                print(f"❌ Error en '{movie.title}': {e}")

        db.session.commit()
        print(f"\n🏁 Proceso finalizado. {count} películas actualizadas.")

if __name__ == "__main__":
    # 1. Intentar arreglar la estructura
    if force_add_columns():
        # 2. Si la estructura está bien, actualizar datos
        update_movies_metadata()