# Script para reparar tabla de solicitudes
import sqlite3
import os

def repair_requests_table():
    # Buscar base de datos
    db_path = 'instance/bus_station.db'
    if not os.path.exists(db_path):
        db_path = 'bus_station.db'

    print(f"🔧 Reparando: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Agregar columna trailer_url
        cursor.execute("ALTER TABLE movie_requests ADD COLUMN trailer_url VARCHAR(500)")
        
        conn.commit()
        conn.close()
        print("✅ Columna agregada.")
        
    except sqlite3.OperationalError as e:
        print(f"Nota: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    repair_requests_table()