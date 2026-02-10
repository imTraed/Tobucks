# Importar variables de entorno
import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

# Configuración base de la aplicación Flask
class Config:
    """Configuración por defecto compartida"""
    # Clave secreta para firmar sesiones de usuario
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    
    # Desactivar notificaciones de cambios en SQLAlchemy para mejor rendimiento
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    OMDB_API_KEY = os.environ.get("OMDB_API_KEY", "c4a84505")
    GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyB8N--E-B7yFzPLAgu0AQ3zL3Mv2Ae7Wbs")


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///instance/bus_station.db")


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    
    # Para Heroku/PostgreSQL
    # Render y Heroku suelen usar DATABASE_URL; también soportamos DATABASE_URI
    database_url = os.environ.get("DATABASE_URL") or os.environ.get("DATABASE_URI")
    if database_url and database_url.startswith("postgres://"):
        # Heroku usa postgres://, SQLAlchemy 1.4+ necesita postgresql://
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url or "sqlite:///instance/bus_station.db"


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


# Seleccionar configuración según el entorno
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}

# Obtener la configuración activa
def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, config["default"])