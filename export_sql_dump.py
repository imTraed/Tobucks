#!/usr/bin/env python
"""
Script para exportar datos de SQLite a un archivo SQL genérico
Este archivo SQL puede importarse en MySQL, PostgreSQL, etc.
Ejecutar: python export_sql_dump.py
"""

import sqlite3
import os

SQLITE_DB = "instance/bus_station.db"
OUTPUT_FILE = "tobucks_export.sql"

def export_to_sql():
    """Exportar SQLite a archivo SQL"""
    
    if not os.path.exists(SQLITE_DB):
        print(f"❌ Error: No se encontró {SQLITE_DB}")
        return
    
    print(f"📤 Exportando datos desde {SQLITE_DB}...")
    
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("-- Dump de base de datos Tobucks\n")
        f.write("-- Exportado desde SQLite\n")
        f.write("-- Puedes importar esto en MySQL, PostgreSQL, y otros DBMS\n\n")
        
        for table_tuple in tables:
            table = table_tuple[0]
            
            # Obtener estructura de la tabla
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            # Obtener datos
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if not rows:
                continue
            
            # Crear línea de inserción manual
            col_names = [col[1] for col in columns]
            
            f.write(f"\n-- Tabla: {table}\n")
            f.write(f"-- Registros: {len(rows)}\n")
            f.write(f"INSERT INTO {table} ({', '.join(col_names)}) VALUES\n")
            
            for i, row in enumerate(rows):
                values = []
                for val in row:
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, str):
                        # Escapar comillas simples
                        escaped = val.replace("'", "''")
                        values.append(f"'{escaped}'")
                    else:
                        values.append(str(val))
                
                value_str = f"({', '.join(values)})"
                comma = "," if i < len(rows) - 1 else ";"
                f.write(f"  {value_str}{comma}\n")
    
    conn.close()
    
    # Información
    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"✅ Archivo exportado: {OUTPUT_FILE} ({file_size:,} bytes)")
    print(f"📊 Puedes importarlo en PostgreSQL, MySQL, o SQLite con:")
    print(f"   psql -U user -d database < {OUTPUT_FILE}")
    print(f"   mysql -u user -p database < {OUTPUT_FILE}")

if __name__ == "__main__":
    export_to_sql()
