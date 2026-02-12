from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from ..models.models import User, Movie, Genre, db

# Creamos el Blueprint para la API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- RUTA DE PRUEBA ---
@api_bp.route('/ping', methods=['GET'])
def ping():
    """Para probar si el servidor responde"""
    return jsonify({'status': 'success', 'message': 'Servidor funcionando correctamente 🚀'})

# --- LOGIN PARA LA APP MÓVIL ---
@api_bp.route('/login', methods=['POST'])
def api_login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        # Crear token de acceso
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token, user_id=user.id, username=user.username), 200
    
    return jsonify({"msg": "Usuario o contraseña incorrectos"}), 401

# --- OBTENER PELÍCULAS (JSON) ---
@api_bp.route('/movies', methods=['GET'])
def get_movies():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    movies = Movie.query.paginate(page=page, per_page=per_page, error_out=False)
    
    data = []
    for m in movies.items:
        data.append({
            'id': m.id,
            'title': m.title,
            'poster': m.poster,
            'description': m.description,
            'genres': [g.name for g in m.genres]
        })
        
    return jsonify({
        'movies': data,
        'total_pages': movies.pages,
        'current_page': page
    })