from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy.sql.expression import func
import os
import urllib.request
import re
import requests 
from werkzeug.utils import secure_filename
from .. import db
from ..models.models import Movie, Genre, Request
import random
from youtubesearchpython import VideosSearch 
from deep_translator import GoogleTranslator

movies_bp = Blueprint('movies', __name__, url_prefix='/movies')

# CONFIGURACIÓN
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- LÓGICA DE BÚSQUEDA DE TRAILER ---
def get_trailer_logic(title):
    if not title: return None
    search_queries = [f"{title} trailer oficial español latino", f"{title} trailer oficial"]
    
    # 1. Intentar con librería
    try:
        for query in search_queries:
            search = VideosSearch(query, limit=1)
            result = search.result()
            if result['result']: return result['result'][0]['link']
    except: pass

    # 2. Plan B (Scraping)
    try:
        query_encoded = urllib.parse.quote(search_queries[0])
        html_url = f"https://www.youtube.com/results?search_query={query_encoded}"
        with urllib.request.urlopen(html_url) as response:
            html = response.read().decode()
            ids = re.findall(r"watch\?v=(\S{11})", html)
            if ids: return f"https://www.youtube.com/watch?v={ids[0]}"
    except: pass
    
    return None

# --- RUTA 1: CATÁLOGO (CON FILTRO TOTAL DE VISTAS) ---
@movies_bp.route('/list')
def list_movies():
    search = request.args.get('search')
    pending_requests = []
    if current_user.is_authenticated and current_user.is_admin:
        pending_requests = Request.query.filter_by(status='pending').all()

    # 1. BÚSQUEDA (Aquí SÍ mostramos las vistas)
    if search:
        movies = Movie.query.filter(Movie.title.ilike(f'%{search}%')).all()
        return render_template('movies.html', movies=movies, search=search, view_mode='grid', pending_requests=pending_requests)

    main_categories = [] 
    
    # --- FILTRO DE VISTAS ---
    seen_ids = []
    if current_user.is_authenticated:
        seen_ids = [m.id for m in current_user.seen_list]

    # A) RECOMENDADO PARA TI
    if current_user.is_authenticated and current_user.preferences:
        user_genre_ids = [p.genre_id for p in current_user.preferences]
        if user_genre_ids:
            recs = Movie.query.join(Movie.genres)\
                .filter(Genre.id.in_(user_genre_ids))\
                .filter(Movie.id.notin_(seen_ids))\
                .order_by(func.random()).limit(15).all()
            if recs: main_categories.append({"title": "Recomendado para Ti", "movies": recs})

    # B) NOVEDADES
    if current_user.is_authenticated:
        recent = Movie.query.filter(Movie.id.notin_(seen_ids)).order_by(func.random()).limit(15).all()
    else:
        recent = Movie.query.order_by(func.random()).limit(15).all()
        
    if recent: main_categories.append({"title": "Novedades", "movies": recent})

    # C) POR GÉNEROS
    genres = Genre.query.join(Movie.genres).group_by(Genre.id).all()
    random.shuffle(genres) 
    
    for genre in genres:
        query = Movie.query.join(Movie.genres).filter(Genre.id == genre.id)
        if current_user.is_authenticated and seen_ids:
            query = query.filter(Movie.id.notin_(seen_ids))
        g_movies = query.order_by(func.random()).limit(15).all()
        if g_movies: 
            main_categories.append({"title": genre.name, "movies": g_movies})

    return render_template('movies.html', categories=main_categories, view_mode='stream', pending_requests=pending_requests)

# --- RUTA 2: VER PELÍCULA ---
@movies_bp.route('/view/<int:movie_id>')
def view_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    related = []
    if movie.genres:
        genre_id = movie.genres[0].id
        query = Movie.query.join(Movie.genres).filter(Genre.id == genre_id, Movie.id != movie.id)
        related = query.limit(6).all()
        
    return render_template('view_movie.html', movie=movie, related_movies=related)

# --- MARCAR COMO VISTA ---
@movies_bp.route('/toggle_seen/<int:movie_id>', methods=['POST'])
@login_required
def toggle_seen(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie in current_user.seen_list:
        current_user.seen_list.remove(movie)
        status = 'unseen'
    else:
        current_user.seen_list.append(movie)
        status = 'seen'
    db.session.commit()
    return jsonify({'status': status, 'success': True})

# --- RUTA 3: AGREGAR ---
@movies_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_movie():
    genres = Genre.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        trailer_url = request.form.get('trailer_url')
        
        existing_movie = Movie.query.filter(Movie.title.ilike(title.strip())).first()
        if existing_movie:
            return render_template('add_movie.html', genres=genres, existing_movie=existing_movie)

        poster_path = None
        if 'poster' in request.files:
            file = request.files['poster']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                poster_path = f'uploads/{filename}'
        
        poster_url_hidden = request.form.get('poster_url')
        if not poster_path and poster_url_hidden:
            try:
                img_data = requests.get(poster_url_hidden).content
                safe_title = secure_filename(title)
                filename = f"{safe_title}_{random.randint(1000,9999)}.jpg"
                if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)
                with open(os.path.join(UPLOAD_FOLDER, filename), 'wb') as f: f.write(img_data)
                poster_path = f'uploads/{filename}'
            except: pass

        if current_user.is_admin:
            new_movie = Movie(title=title, description=description, poster=poster_path, trailer_url=trailer_url)
            for g_id in request.form.getlist('genres'):
                genre = Genre.query.get(g_id)
                if genre: new_movie.genres.append(genre)
            db.session.add(new_movie)
            db.session.commit()
            flash('Película agregada al catálogo.', 'success')
        else:
            if not trailer_url: trailer_url = get_trailer_logic(title)
            new_req = Request(title=title, description=description, trailer_url=trailer_url, poster=poster_path, user_id=current_user.id)
            db.session.add(new_req)
            db.session.commit()
            flash('Solicitud enviada.', 'info')
        return redirect(url_for('movies.list_movies'))
    return render_template('add_movie.html', genres=genres)

# --- RUTAS API ---
@movies_bp.route('/search_omdb', methods=['POST'])
@login_required
def search_omdb():
    data = request.get_json()
    title = data.get('title')
    api_key = current_app.config.get('OMDB_API_KEY') or "TU_API_KEY_AQUI" 
    if not title: return jsonify({'error': 'Falta título'}), 400
    try:
        url = f"http://www.omdbapi.com/?apikey={api_key}&t={title}"
        response = requests.get(url)
        movie_data = response.json()
        if movie_data.get('Response') == 'True':
            translator = GoogleTranslator(source='auto', target='es')
            if 'Plot' in movie_data and movie_data['Plot'] != "N/A":
                try: movie_data['Plot'] = translator.translate(movie_data['Plot'])
                except: pass
            if 'Genre' in movie_data and movie_data['Genre'] != "N/A":
                try: movie_data['Genre'] = translator.translate(movie_data['Genre'])
                except: pass
        return jsonify(movie_data)
    except Exception as e: return jsonify({'error': str(e)}), 500

@movies_bp.route('/find_trailer_api', methods=['POST'])
@login_required
def find_trailer_api():
    if not current_user.is_admin: return jsonify({'error': 'No autorizado'}), 403
    data = request.get_json()
    title = data.get('title', '').strip()
    url = get_trailer_logic(title)
    if url: return jsonify({'url': url, 'success': True})
    return jsonify({'error': 'No encontrado'}), 404

# --- GESTIÓN ---
@movies_bp.route('/add_genre', methods=['GET', 'POST'])
@login_required
def add_genre():
    if not current_user.is_admin: return redirect(url_for('movies.list_movies'))
    if request.method == 'POST':
        name = request.form.get('name')
        if name and not Genre.query.filter_by(name=name).first():
            db.session.add(Genre(name=name))
            db.session.commit()
            flash('Género agregado', 'success')
    return render_template('add_genre.html', genres=Genre.query.all())

@movies_bp.route('/request/approve/<int:request_id>', methods=['POST'])
@login_required
def approve_request(request_id):
    if not current_user.is_admin: return redirect(url_for('main.index'))
    req = Request.query.get_or_404(request_id)
    final_title = request.form.get('title') or req.title
    final_desc = request.form.get('description') or req.description
    final_trailer = request.form.get('trailer_url') or req.trailer_url
    new_movie = Movie(title=final_title, description=final_desc, trailer_url=final_trailer, poster=req.poster)
    req.status = 'approved'
    db.session.add(new_movie)
    db.session.commit()
    flash('Aprobada.', 'success')
    return redirect(url_for('movies.list_movies'))

@movies_bp.route('/request/reject/<int:request_id>', methods=['POST'])
@login_required
def reject_request(request_id):
    if not current_user.is_admin: return redirect(url_for('main.index'))
    req = Request.query.get_or_404(request_id)
    req.status = 'rejected'
    db.session.commit()
    flash('Rechazada.', 'warning')
    return redirect(url_for('movies.list_movies'))

@movies_bp.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def edit_movie(movie_id):
    if not current_user.is_admin: return redirect(url_for('movies.list_movies'))
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        movie.title = request.form.get('title')
        movie.description = request.form.get('description')
        movie.trailer_url = request.form.get('trailer_url')
        try: movie.rating = float(request.form.get('rating') or 0)
        except: movie.rating = 0.0
        movie.runtime = request.form.get('runtime')
        if request.form.get('delete_poster'): movie.poster = None
        if 'poster' in request.files:
            file = request.files['poster']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                movie.poster = f'uploads/{filename}'
        movie.genres = []
        for g_id in request.form.getlist('genres'):
            g = Genre.query.get(g_id)
            if g: movie.genres.append(g)
        db.session.commit()
        return redirect(url_for('movies.view_movie', movie_id=movie.id))
    return render_template('edit_movie.html', movie=movie, genres=Genre.query.all())

@movies_bp.route('/delete/<int:movie_id>', methods=['POST'])
@login_required
def delete_movie(movie_id):
    if not current_user.is_admin: return redirect(url_for('movies.list_movies'))
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Eliminada.', 'success')
    return redirect(url_for('movies.list_movies'))