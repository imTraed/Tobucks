# Script para agregar columna poster a películas
import sqlite3
import os

# Localizar base de datos
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'bus_station.db')
print(f'BD: {db_path}')

if not os.path.exists(db_path):
    print('Base de datos no encontrada.')
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Verificar columnas actuales
cur.execute("PRAGMA table_info(movies);")
cols = [row[1] for row in cur.fetchall()]
print(f'Columnas: {cols}')

# Agregar columna poster si no existe
if 'poster' in cols:
    print('Columna poster ya existe.')
else:
    print('Agregando columna poster...')
    try:
        cur.execute("ALTER TABLE movies ADD COLUMN poster VARCHAR(200);")
        conn.commit()
        print('✅ Columna agregada.')
    except Exception as e:
        print(f'Error: {e}')

conn.close()
