"""IA Concierge: Auto-Importación con Normalización de Géneros (Español)"""
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
import os
import json
import uuid
import requests
import re
import unicodedata
from groq import Groq
from .. import db
from ..models.models import Movie, Genre

# --- CONFIGURACIÓN DE LIBRERÍAS EXTERNAS ---
try:
    from deep_translator import GoogleTranslator
    from youtubesearchpython import VideosSearch
except ImportError:
    print("⚠️ ADVERTENCIA: Librerías extra no instaladas.")
    GoogleTranslator = None
    VideosSearch = None

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

# --- DICCIONARIO MAESTRO DE GÉNEROS (Inglés -> Español) ---
# Esto evita duplicados. Ajusta los nombres de la derecha a CÓMO LOS TIENES en tu BD.
GENRE_MAP = {
    "Action": "Acción",
    "Adventure": "Aventura",
    "Animation": "Animación",
    "Biography": "Biografía",
    "Comedy": "Comedia",
    "Crime": "Crimen",
    "Documentary": "Documental",
    "Drama": "Drama",
    "Family": "Familia",
    "Fantasy": "Fantasía",
    "Film-Noir": "Cine Negro",
    "History": "Historia",
    "Horror": "Terror",
    "Music": "Música",
    "Musical": "Musical",
    "Mystery": "Misterio",
    "Romance": "Romance",
    "Sci-Fi": "Ciencia Ficción",
    "Short": "Cortometraje",
    "Sport": "Deporte",
    "Superhero": "Superhéroes",
    "Thriller": "Suspenso",
    "War": "Guerra",
    "Western": "Western"
}

# --- UTILIDADES ---
def manual_slugify(text):
    if not text: return None
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).lower()
    return re.sub(r'[-\s]+', '-', text).strip('-')

def download_poster(img_url):
    if not img_url or img_url == 'N/A' or not img_url.startswith('http'): return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(img_url, headers=headers, timeout=5)
        if resp.status_code == 200:
            ext = os.path.splitext(img_url.split('?')[0])[1] or '.jpg'
            if len(ext) > 5: ext = '.jpg'
            filename = f"{uuid.uuid4().hex}{ext}"
            save_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(save_dir, exist_ok=True)
            with open(os.path.join(save_dir, filename), 'wb') as f:
                f.write(resp.content)
            return f"uploads/{filename}"
    except: return None

def get_trailer_url(title, year):
    if not VideosSearch: return None
    try:
        query = f"{title} {year} trailer sub español"
        videos_search = VideosSearch(query, limit=1)
        results = videos_search.result()
        if results['result']:
            return results['result'][0]['link']
    except: pass
    return None

def translate_text(text):
    if not text or text == "N/A": return "Sin descripción."
    if not GoogleTranslator: return text
    try:
        return GoogleTranslator(source='auto', target='es').translate(text)
    except: return text

# --- RUTAS ---

@ai_bp.route("/concierge")
@login_required
def concierge():
    return render_template("ai_concierge.html")

@ai_bp.route("/ask_adventure", methods=["POST"])
@login_required
def ask_adventure():
    data = request.json
    narrative = data.get('narrative', '')
    era = data.get('era', 'all') 

    groq_key = current_app.config.get('GROQ_API_KEY') or os.environ.get('GROQ_API_KEY')
    omdb_key = current_app.config.get('OMDB_API_KEY')

    if not groq_key: return jsonify({'error': 'Falta configuración de IA'}), 500

    # 1. FILTRO LOCAL
    local_instruction = ""
    try:
        query = Movie.query
        if era == 'old': query = query.filter(Movie.year > 0, Movie.year < 1980)
        elif era == '80s': query = query.filter(Movie.year.between(1980, 1989))
        elif era == '90s': query = query.filter(Movie.year.between(1990, 1999))
        elif era == '2000s': query = query.filter(Movie.year.between(2000, 2010))
        elif era == 'recent': query = query.filter(Movie.year > 2010)
        
        local_movies = query.limit(50).all()
        if local_movies:
            titulos = ", ".join([m.title for m in local_movies])
            local_instruction = f"CATÁLOGO LOCAL: [{titulos}]"
        else:
            local_instruction = "CATÁLOGO VACÍO."
    except: local_instruction = "Sugiere libremente."

    # 2. CONSULTA A GROQ
    try:
        client = Groq(api_key=groq_key)
        system_prompt = f"""
        Eres experto en cine.
        {local_instruction}
        INSTRUCCIONES:
        1. Usuario quiere: "{narrative}" (Época: {era}).
        2. Prioriza catálogo local. Si no, sugiere externos.
        3. Devuelve JSON con 3 "top_picks" y 5 "also_like".
        REGLA DE ORO: Responde ÚNICAMENTE en formato JSON. 
        Usa estrictamente estas llaves en minúsculas y sin tildes: 
        "title" para el nombre de la película y "reason" para el motivo.
        """
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Genera recomendaciones JSON."}
            ],
            temperature=0.6,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        raw_data = json.loads(completion.choices[0].message.content)
        print("------------------------------------")
        print("🤖 LA IA SUGIRIÓ ESTO:", raw_data)
        print("------------------------------------")
    except: return jsonify({'error': 'Error IA'}), 500

    # 3. AUTO-IMPORTADOR (CON NORMALIZACIÓN DE GÉNEROS)
    def magic_import(items):
        final_list = []
        for item in items:
            # 1. Obtención flexible del título
            title = item.get('title') or item.get('título')
            if not title: continue
            
            # 2. Búsqueda en base de datos local
            movie = Movie.query.filter(Movie.title.ilike(title)).first()
            if not movie:
                movie = Movie.query.filter(Movie.title.ilike(f"%{title}%")).first()

            # 3. Importación desde OMDb si no existe localmente
            if not movie and omdb_key:
                try:
                    r = requests.get(f'http://www.omdbapi.com/?t={title}&apikey={omdb_key}', timeout=5).json()
                    
                    if r.get('Response') == 'True':
                        safe_title = r.get('Title')
                        
                        # Procesamiento de Año (limpieza de formatos como "2019–")
                        year_str = r.get('Year', '0')
                        match = re.search(r'\d{4}', str(year_str))
                        clean_year = int(match.group()) if match else 0

                        # --- CREACIÓN DEL OBJETO MOVIE CON TODOS LOS CAMPOS ---
                        movie = Movie(
                            title=safe_title,
                            slug=manual_slugify(safe_title),
                            description=translate_text(r.get('Plot')), # Sinopsis traducida
                            poster=download_poster(r.get('Poster')),   # Descarga de portada
                            year=clean_year,                           # Año de lanzamiento
                            rating=float(r.get('imdbRating', 0)) if r.get('imdbRating') != 'N/A' else 0.0,
                            trailer_url=get_trailer_url(safe_title, clean_year), # Búsqueda de trailer
                            runtime=r.get('Runtime', 'N/A')            # Duración
                        )
                        
                        # --- PASO CRÍTICO: Agregar a la sesión ANTES de los géneros ---
                        # Esto evita el SAWarning: Object not in session
                        db.session.add(movie)
                        db.session.flush() # Sincroniza el objeto para permitir relaciones

                        # 4. Gestión de Géneros Dinámicos
                        if r.get('Genre') and r.get('Genre') != 'N/A':
                            genre_names = r.get('Genre').split(',')
                            
                            for g_name in genre_names:
                                raw_name = g_name.strip()
                                # Normalización/Traducción (ej. Comedy -> Comedia)
                                translated_name = GENRE_MAP.get(raw_name, raw_name)
                                
                                # Buscar o crear el género en la BD
                                g_db = Genre.query.filter(Genre.name.ilike(translated_name)).first()
                                
                                if not g_db:
                                    g_db = Genre(name=translated_name)
                                    db.session.add(g_db)
                                    db.session.flush() # Asegura que el género tenga ID
                                
                                # Vincular género a la película
                                if g_db not in movie.genres:
                                    movie.genres.append(g_db)

                        # 5. Guardado final de la transacción
                        db.session.commit()
                        print(f"✨ Importación exitosa: {safe_title}")
                        
                except Exception as e:
                    db.session.rollback() # Revierte cambios si hay error (evita UniqueViolation)
                    print(f"⚠️ Error importando '{title}': {e}")
                    movie = None

            # 6. Construcción de la lista de respuesta para la interfaz
            if movie:
                # Usamos el primer género disponible para la tarjeta de previsualización
                g_name = movie.genres[0].name if movie.genres else "Cine"
                final_list.append({
                    'id': movie.id, 
                    'title': movie.title, 
                    'poster': movie.poster, 
                    'genres': [g_name], 
                    'reason': item.get('reason') or item.get('razón') or 'Recomendación IA',
                    'year': movie.year,
                    'runtime': movie.runtime
                })
        return final_list

    # Ejecución del importador para las sugerencias de la IA
    top = magic_import(raw_data.get('top_picks', []))
    also = magic_import(raw_data.get('also_like', []))

    # Manejo de listas vacías para evitar errores 404 en el frontend
    if not top and not also:
        print("⚠️ Debug: Las listas regresaron vacías desde el importador.")
        return jsonify({
            'top_picks': [], 
            'also_like': [], 
            'debug_msg': 'La IA sugirió títulos, pero no se pudieron importar o encontrar.'
        }), 200 

    return jsonify({'top_picks': top, 'also_like': also})