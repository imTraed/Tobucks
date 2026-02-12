"""Rutas para recomendaciones de películas"""
from flask import Blueprint, render_template, request, url_for, jsonify
from flask_login import login_required, current_user
from ..models.models import Movie, Genre

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations')
@login_required
def recommendations():
    """Mostrar recomendaciones según preferencias del usuario"""
    
    # 1. Obtener géneros preferidos del usuario
    user_preferences = [pref.genre_id for pref in current_user.preferences]
    
    # Si no hay preferencias, devolver vacío
    if not user_preferences:
        if request.args.get('json'):
            return jsonify({'movies': []})
        return render_template('recommendations.html', 
                               recommendations=[], 
                               current_page=1, total_pages=1)

    # 2. Filtrar películas por géneros preferidos
    base_query = Movie.query.filter(Movie.genres.any(Genre.id.in_(user_preferences)))

    # 3. Excluir películas ya vistas
    seen_ids = [m.id for m in current_user.seen_list]
    if seen_ids:
        base_query = base_query.filter(Movie.id.notin_(seen_ids))
    
    # 4. Paginación (5 películas por página)
    page = request.args.get('page', 1, type=int)
    pagination = base_query.paginate(page=page, per_page=5, error_out=False) 
    list_movies = pagination.items

    # 5. Respuesta JSON (Útil si usas scroll infinito o para la App Móvil)
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

    # 6. Renderizar plantilla (LIMPIO: Sin nodos ni edges)
    return render_template(
        'recommendations.html',
        recommendations=list_movies,
        current_page=page,
        total_pages=pagination.pages
    )