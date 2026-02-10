# Script para agregar columna 'trailer_url' a películas
import sqlite3

def fix_database():
    print("🔧 Agregando columna 'trailer_url'...")
    try:
        # Conectar a base de datos
        conn = sqlite3.connect('instance/bus_station.db') 
        cursor = conn.cursor()
        
        # Agregar columna
        cursor.execute("ALTER TABLE movies ADD COLUMN trailer_url VARCHAR(500)")
        conn.commit()
        print("✅ Columna creada.")
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Nota: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_database()