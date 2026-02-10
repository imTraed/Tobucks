#!/usr/bin/env python
"""
Script para exportar datos de SQLite a JSON
Esto facilita la migración a cualquier BD
Ejecutar: python export_json_dump.py
"""

import sqlite3
import json
import os
from datetime import datetime

SQLITE_DB = "instance/bus_station.db"
OUTPUT_FILE = "tobucks_data_export.json"

def export_to_json():
    """Exportar SQLite a JSON"""
    
    if not os.path.exists(SQLITE_DB):
        print(f"❌ Error: No se encontró {SQLITE_DB}")
        return
    
    print(f"📤 Exportando datos desde {SQLITE_DB}...")
    
    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [t[0] for t in cursor.fetchall()]
    
    export_data = {
        "export_date": datetime.now().isoformat(),
        "database": "tobucks",
        "source": "SQLite bus_station.db",
        "tables": {}
    }
    
    total_records = 0
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        records = [dict(row) for row in rows]
        
        # Convertir tipos no serializables
        for record in records:
            for key, value in record.items():
                if isinstance(value, bytes):
                    record[key] = value.decode('utf-8', errors='replace')
        
        if records:
            export_data["tables"][table] = {
                "count": len(records),
                "records": records
            }
            total_records += len(records)
            print(f"✅ {table}: {len(records)} registros")
        else:
            print(f"⏭️  {table}: (sin datos)")
    
    conn.close()
    
    # Guardar a JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(OUTPUT_FILE)
    print(f"\n✅ Archivo exportado: {OUTPUT_FILE} ({file_size:,} bytes)")
    print(f"📊 Total de registros: {total_records}")
    print(f"\nPuedes importar este JSON en PostgreSQL, MySQL o cualquier BD")

if __name__ == "__main__":
    export_to_json()
