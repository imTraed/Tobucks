import pandas as pd
from sqlalchemy import create_engine, text
import os

# --- 1. CONFIGURACIÓN ---

# Buscamos la base de datos en la carpeta 'instance'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'bus_station.db')
LOCAL_DB = f'sqlite:///{DB_PATH}'

# ⚠️ PEGA AQUÍ TU URL EXTERNA DE RENDER (La misma que usaste antes)
RENDER_DB_URL = "postgresql://tobucks_db_user:YZWrqS2QHO5xqVC31GaIFQOXTMurWPoi@dpg-d65nfa94tr6s73d67k40-a.oregon-postgres.render.com/tobucks_db" 

# Corrección automática para Render
if RENDER_DB_URL.startswith("postgres://"):
    RENDER_DB_URL = RENDER_DB_URL.replace("postgres://", "postgresql://", 1)

# --- 2. TABLAS A MIGRAR ---
tables_to_migrate = [
    'genre', 'genres',
    'user', 'users',
    'movie', 'movies',
    'movie_genre', 'movie_genres',
    'seen_movies',
    'preference', 'user_preferences',
    'request', 'requests'
]

def migrate():
    print(f"📂 Buscando base de datos en: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("❌ ERROR: No encuentro el archivo bus_station.db.")
        return

    print("🚀 Iniciando conexión...")
    try:
        source_engine = create_engine(LOCAL_DB)
        dest_engine = create_engine(RENDER_DB_URL)
        print("✅ Conexión establecida.")
        
        # --- PASO EXTRA: ARREGLAR TAMAÑO DE CONTRASEÑA ---
        print("🔧 Ajustando la base de datos de Render para contraseñas largas...")
        with dest_engine.connect() as conn:
            # Ampliamos la columna password a TEXT (sin límite) para que quepan tus hashes
            conn.execute(text("ALTER TABLE users ALTER COLUMN password TYPE TEXT;"))
            conn.commit()
            print("✅ Esquema de usuarios actualizado.")
            
    except Exception as e:
        # Si falla el ALTER TABLE, puede ser que ya esté arreglado o la tabla no exista aún.
        # Continuamos con la migración por si acaso.
        print(f"⚠️ Nota sobre esquema: {e}")

    print("\n--- COMENZANDO TRANSFERENCIA ---")
    for table in tables_to_migrate:
        try:
            df = pd.read_sql_table(table, source_engine)
            
            if df.empty:
                print(f"⚪ Tabla '{table}' vacía. Saltando.")
                continue

            print(f"📦 Procesando '{table}' ({len(df)} registros)...")
            
            # Subimos los datos
            df.to_sql(table, dest_engine, if_exists='append', index=False, method='multi', chunksize=1000)
            print(f"   ✅ {len(df)} registros subidos correctamente.")
            
        except ValueError:
            pass # La tabla no existe en local
        except Exception as e:
            if "UniqueViolation" in str(e) or "unique constraint" in str(e):
                print(f"   ⚠️ Datos ya existentes en '{table}'.")
            elif "ForeignKeyViolation" in str(e):
                print(f"   ❌ Error de dependencia en '{table}': Faltan los datos padre (ej. Usuarios).")
            else:
                print(f"   ❌ Error en '{table}': {str(e).splitlines()[0]}")

    print("\n🏁 --- MIGRACIÓN FINALIZADA --- 🏁")

if __name__ == "__main__":
    migrate()