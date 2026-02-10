"""Rutas para recomendaciones de películas"""
from flask import Blueprint, render_template, request, url_for, jsonify
from flask_login import login_required, current_user
from ..models.models import Movie, Genre

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations')
@login_required
def recommendations():
    """Mostrar recomendaciones según preferencias del usuario"""
    
    # Obtener géneros preferidos del usuario
    user_preferences = [pref.genre_id for pref in current_user.preferences]
    
    # Si no hay preferencias, devolver vacío
    if not user_preferences:
        if request.args.get('json'):
            return jsonify({'movies': []})
        return render_template('recommendations.html', 
                               recommendations=[], 
                               nodes=[], edges=[], 
                               current_page=1, total_pages=1)

    # Filtrar películas por géneros preferidos
    base_query = Movie.query.filter(Movie.genres.any(Genre.id.in_(user_preferences)))

    # Excluir películas ya vistas
    seen_ids = [m.id for m in current_user.seen_list]
    if seen_ids:
        base_query = base_query.filter(Movie.id.notin_(seen_ids))
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    pagination = base_query.paginate(page=page, per_page=5, error_out=False) 
    list_movies = pagination.items

    # Respuesta JSON para scroll infinito
    if request.args.get('json'):
        movies_data = [
            {
                'id': movie.id,
                'title': movie.title,
                'poster': movie.poster,
                'description': movie.description,
                'genres': [{'name': g.name} for g in movie.genres]
            }
            for movie in list_movies
        ]
        return jsonify({'movies': movies_data})

    # Construir grafo de películas y géneros
    graph_movies = base_query.all()
    nodes = []
    edges = []
    
    # Nodo del usuario
    nodes.append({
        'id': 'user_node',
        'label': current_user.username.upper(),
        'shape': 'circle',
        'size': 60,
        'color': {
            'background': '#FFD700', 
            'border': '#FFFFFF',
            'highlight': {'background': '#FFD700', 'border': '#FFFFFF'}
        },
        'font': {
            'size': 14, 'color': '#000000', 'face': 'Segoe UI', 'bold': True, 'vadjust': 0
        },
        'borderWidth': 3,
        'shadow': {'enabled': True, 'color': 'rgba(255, 215, 0, 0.7)', 'size': 35, 'x': 0, 'y': 0}
    })

    # Identificar géneros activos para el grafo
    active_genre_ids = set()
    for movie in graph_movies:
        for genre in movie.genres:
            if genre.id in user_preferences:
                active_genre_ids.add(genre.id)

    # --- LÓGICA: Detectar si hay muchos géneros para simplificar la vista ---
    # Si hay más de 13 categorías seleccionadas, activamos el modo simple
    simple_mode = len(active_genre_ids) > 13

    # Nodos de géneros
    for genre_id in active_genre_ids:
        genre = Genre.query.get(genre_id)
        if genre:
            g_node_id = f"genre_{genre.id}"
            nodes.append({
                'id': g_node_id,
                'label': genre.name.upper(),
                'shape': 'text', 
                'font': {
                    'size': 24, 
                    'color': '#FFD700', 
                    'face': 'Segoe UI', 
                    'weight': 'bold'
                },
                'margin': 10
            })
            # Conectar usuario con género
            edges.append({
                'from': 'user_node', 'to': g_node_id, 
                'color': '#FFD700', 
                'width': 3
            })

    # Nodos de películas
    for movie in graph_movies:
        m_node_id = f"movie_{movie.id}"
        
        if simple_mode:
            # --- MODO SIMPLE (> 13 géneros) ---
            # Círculo blanco, fondo negro, letras blancas, destello blanco.
            nodes.append({
                'id': m_node_id,
                'label': movie.title,  # Mostramos el título
                'shape': 'ellipse',    # Usamos 'ellipse' para que el texto quepa bien dentro
                'color': {
                    'background': '#000000', # Fondo Negro puro
                    'border': '#FFFFFF',     # Borde Blanco puro
                    'highlight': {
                        'background': '#000000', 
                        'border': '#FFD700', # Borde dorado al seleccionar
                        'borderWidth': 4
                    }
                },
                'font': {
                    'color': '#FFFFFF', # Letras Blancas
                    'size': 16,
                    'face': 'Segoe UI',
                    'weight': 'bold'
                },
                'borderWidth': 3,
                # EL DESTELLO BLANCO
                'shadow': {
                    'enabled': True,
                    'color': '#FFFFFF', # Blanco puro
                    'size': 25,         # Grande y difuminado
                    'x': 0, 'y': 0
                }
            })
        else:
            # --- MODO DETALLADO (<= 13 géneros) ---
            # Con imágenes
            image_url = url_for('static', filename=movie.poster) if movie.poster else None
            
            nodes.append({
                'id': m_node_id,
                'title': movie.title, 
                'shape': 'image' if image_url else 'box', 
                'image': image_url,
                'label': '', 
                'size': 40,
                'shapeProperties': {'useBorderWithImage': True},
                'color': {
                    'border': '#333333', 
                    'background': '#111111',
                    'highlight': {'border': '#FFD700'}
                },
                'borderWidth': 2,
                'shadow': {'enabled': True, 'color': 'rgba(255, 255, 255, 0.5)', 'size': 25, 'x': 0, 'y': 0}
            })

        # Conectar película con géneros
        for genre in movie.genres:
            if genre.id in active_genre_ids:
                edges.append({
                    'from': f"genre_{genre.id}", 
                    'to': m_node_id,
                    # En modo simple, líneas más sutiles para resaltar el destello
                    'color': 'rgba(255, 255, 255, 0.3)' if simple_mode else 'rgba(255, 255, 255, 0.1)',
                    'width': 1
                })

    return render_template(
        'recommendations.html',
        recommendations=list_movies,
        current_page=page,
        total_pages=pagination.pages,
        nodes=nodes,
        edges=edges
    )