import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Extensiones globales
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- CONFIGURACIÓN DE BASE DE DATOS ---
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        # --- MODO NUBE (Render) ---
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print("✅ MODO NUBE: Conectado a PostgreSQL")
    else:
        # --- MODO LOCAL (PC) ---
        basedir = os.path.abspath(os.path.dirname(__file__))
        project_root = os.path.dirname(basedir)
        
        instance_db = os.path.join(project_root, 'instance', 'bus_station.db')
        root_db = os.path.join(project_root, 'bus_station.db')
        default_db = os.path.join(project_root, 'db.sqlite3')

        if os.path.exists(instance_db):
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{instance_db}'
            print(f"📂 MODO LOCAL: Usando base de datos en INSTANCE")
        elif os.path.exists(root_db):
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{root_db}'
            print(f"📂 MODO LOCAL: Usando base de datos en RAÍZ")
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{default_db}'
            print(f"⚠️ MODO LOCAL: Usando nueva base de datos: {default_db}")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- CLAVES SECRETAS (Protegidas) ---
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'desarrollo-key-segura')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-desarrollo-key')
    
    # --- APIs EXTERNAS (Sin claves hardcodeadas) ---
    app.config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
    app.config['OMDB_API_KEY'] = os.getenv('OMDB_API_KEY')

    # --- INICIALIZAR EXTENSIONES ---
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "users.login"
    
    CORS(app)
    JWTManager(app)

    # Cargar usuario
    from .models.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- REGISTRO DE BLUEPRINTS ---
    from .routes.main import main_bp
    from .routes.users import users_bp
    from .routes.movies import movies_bp
    from .routes.recommendations import recommendations_bp
    from .routes.ai_concierge import ai_bp
    from .routes.api import api_bp
    from .routes.preferences import preferences_bp 
    
    app.register_blueprint(preferences_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(api_bp)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
# ... (código anterior de registro de blueprints)

    # --- AUTO-MIGRACIÓN PARA RENDER (SOLUCIÓN SIN SHELL) ---
    with app.app_context():
        from sqlalchemy import text
        try:
            # 1. Intentar agregar la columna year (por si acaso no se ha hecho)
            try:
                db.session.execute(text("ALTER TABLE movies ADD COLUMN year INTEGER DEFAULT 0"))
                db.session.commit()
                print("✅ Columna 'year' añadida.")
            except:
                db.session.rollback()

            # 2. ARREGLO CRÍTICO: Sincronizar el contador de IDs en PostgreSQL
            # Esto busca el ID más alto y le dice al contador que empiece desde ahí + 1
            if os.getenv('DATABASE_URL'): # Solo si estamos en la nube (Postgres)
                db.session.execute(text("SELECT setval('movies_id_seq', (SELECT MAX(id) FROM movies))"))
                db.session.commit()
                print("✅ Secuencia de IDs sincronizada en Postgres.")

        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Nota de mantenimiento: {e}")

    return app