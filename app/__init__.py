"""Inicialización de la aplicación Flask"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Extensiones globales
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    """Crear y configurar la aplicación Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configuración de APIs
    app.config['GOOGLE_API_KEY'] = 'AIzaSyB8N--E-B7yFzPLAgu0AQ3zL3Mv2Ae7Wbs'
    app.config['OMDB_API_KEY'] = 'c4a84505'

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "users.login"

    # Cargar usuario desde sesión
    from .models.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        # Crear tablas de base de datos
        db.create_all()

        # Importar y registrar blueprints (rutas)
        from .routes.main import main_bp
        from .routes.users import users_bp
        from .routes.movies import movies_bp
        from .routes.recommendations import recommendations_bp
        from .routes.ai_concierge import ai_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(users_bp)
        app.register_blueprint(movies_bp)
        app.register_blueprint(recommendations_bp)
        app.register_blueprint(ai_bp)

    return app