# Script para agregar columna 'slug' a películas
import sqlite3
import os

def fix_db():
    # Buscar base de datos
    db_path = 'instance/bus_station.db'
    if not os.path.exists(db_path):
        db_path = 'bus_station.db'

    print(f"Conectando a: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Agregar columna slug
        cursor.execute("ALTER TABLE movies ADD COLUMN slug VARCHAR(150)")
        
        conn.commit()
        conn.close()
        print("✅ Columna 'slug' agregada.")
    except sqlite3.OperationalError as e:
        print(f"Nota: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_db()