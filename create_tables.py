# Script para crear tablas de base de datos
from app import create_app, db
from app.models.models import Request

app = create_app()

# Crear todas las tablas
with app.app_context():
    db.create_all()
    print("✅ Tablas creadas.")