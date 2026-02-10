#!/usr/bin/env python
"""
Script para migrar datos de SQLite a PostgreSQL
Ejecutar: python migrate_to_postgres.py
"""

import os
import sys
import sqlite3
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Configuración
SQLITE_DB = "instance/bus_station.db"
POSTGRES_URI = os.environ.get("DATABASE_URI", "postgresql://user:password@localhost:5432/tobucks_db")

def get_sqlite_connection():
    """Conectar a SQLite"""
    if not os.path.exists(SQLITE_DB):
        print(f"❌ Error: No se encontró {SQLITE_DB}")
        sys.exit(1)
    return sqlite3.connect(SQLITE_DB)

def get_postgres_connection(uri):
    """Conectar a PostgreSQL"""
    try:
        # Parsear URI de PostgreSQL
        uri = uri.replace("postgresql://", "")
        parts = uri.split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        
        return psycopg2.connect(
            host=host_db[0],
            user=user_pass[0],
            password=user_pass[1],
            database=host_db[1]
        )
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        sys.exit(1)

def migrate_data():
    """Migrar datos de SQLite a PostgreSQL"""
    
    print("🔄 Iniciando migración SQLite → PostgreSQL...")
    print(f"📍 SQLite: {SQLITE_DB}")
    print(f"📍 PostgreSQL: {POSTGRES_URI}\n")
    
    sqlite_conn = get_sqlite_connection()
    pg_conn = get_postgres_connection(POSTGRES_URI)
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    try:
        # Tablas a migrar en orden (respetando FK)
        tables_to_migrate = [
            'genres',
            'users',
            'movies',
            'movie_genres',
            'user_preferences',
            'requests',
            'seen_movies'
        ]
        
        total_records = 0
        
        for table in tables_to_migrate:
            # Obtener datos de SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"⏭️  {table}: No hay datos")
                continue
            
            # Obtener estructura
            sqlite_cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in sqlite_cursor.fetchall()]
            col_names = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            
            # Insertar en PostgreSQL
            insert_query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
            
            for row in rows:
                try:
                    pg_cursor.execute(insert_query, row)
                except psycopg2.Error as e:
                    print(f"⚠️  Error insertando en {table}: {e}")
                    continue
            
            pg_conn.commit()
            record_count = len(rows)
            total_records += record_count
            print(f"✅ {table}: {record_count} registros migrados")
        
        print(f"\n✨ Migración completada: {total_records} registros total\n")
        
    except Exception as e:
        print(f"❌ Error durante migración: {e}")
        pg_conn.rollback()
        sys.exit(1)
    
    finally:
        sqlite_conn.close()
        pg_cursor.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_data()
