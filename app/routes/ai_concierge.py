"""IA Concierge: recomendaciones de películas con IA Gemini"""
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import requests
import json
import os
import uuid
import re
from .. import db
from ..models.models import Movie, Genre

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

def download_poster(img_url):
    """Descargar y guardar póster de película"""
    if not img_url or img_url == 'N/A' or not img_url.startswith('http'): 
        return None
    try:
        resp = requests.get(img_url, timeout=10)
        if resp.status_code == 200:
            ext = os.path.splitext(img_url.split('?')[0])[1] or '.jpg'
            if len(ext) > 5: ext = '.jpg'
            filename = f"{uuid.uuid4().hex}{ext}"
            save_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(save_dir, exist_ok=True)
            with open(os.path.join(save_dir, filename), 'wb') as f:
                f.write(resp.content)
            return f"uploads/{filename}"
    except: 
        return None

@ai_bp.route("/concierge")
@login_required
def concierge():
    """Página del asistente IA"""
    return render_template("ai_concierge.html")

@ai_bp.route("/ask_adventure", methods=["POST"])
@login_required
def ask_adventure():
    """Procesar solicitud de recomendaciones IA"""
    data = request.json
    narrative_profile = data.get('narrative', '')

    api_key = current_app.config.get('GOOGLE_API_KEY')
    omdb_key = current_app.config.get('OMDB_API_KEY')

    if not api_key: 
        return jsonify({'error': 'Falta API Key de Google'}), 500

    # Obtener catálogo de películas disponibles
    existing_movies = Movie.query.with_entities(Movie.title).limit(800).all()
    catalog_list = [m.title for m in existing_movies]
    catalog_str = ", ".join(catalog_list) if catalog_list else "Inventario vacío."

    # Obtener películas ya vistas por el usuario
    seen_titles_str = ""
    if current_user.is_authenticated:
        seen_titles = [m.title for m in current_user.seen_list]
        if seen_titles:
            seen_titles_str = ", ".join(seen_titles[-100:])

    # Configurar IA Gemini
    genai.configure(api_key=api_key)
    
    # Configuración de seguridad
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    # Seleccionar modelo
    chosen_model = 'models/gemini-1.5-flash'
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                chosen_model = m.name
                break
    except: 
        pass

    # Prompt estratégico para IA
    system_instruction = f"""
    Eres un experto en cine.
    
    Perfil del usuario: "{narrative_profile}"
    Catálogo disponible: [{catalog_str}]
    Películas ya vistas: [{seen_titles_str}]

    REGLAS:
    1. NO recomendes películas ya vistas.
    2. Si piden un género/época no en el catálogo, recomienda clásicos mundiales.
    3. Devuelve SOLO JSON válido sin markdown.

    JSON:
    {{
        "top_picks": [
            {{"title": "Título Original", "reason": "Por qué verla en español."}}
        ],
        "also_like": [
            {{"title": "Título Extra"}}
        ]
    }}
    """

    try:
        print(f"🔮 Consultando IA...")
        model = genai.GenerativeModel(chosen_model)
        
        response = model.generate_content(
            system_instruction, 
            safety_settings=safety_settings
        )
        
        # Extraer JSON de la respuesta
        text_response = response.text
        json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
        
        if json_match:
            clean_json = json_match.group(0)
            raw_data = json.loads(clean_json)
        else:
            raise ValueError("JSON inválido.")

    except Exception as e:
        print(f"❌ Error IA: {e}")
        return jsonify({'error': f'Error: {str(e)}'}), 500

    # Procesar películas recomendadas
    def process_movie_list(items_list):
        processed = []
        for item in items_list:
            title = item.get('title')
            reason = item.get('reason', '')
            if not title: 
                continue

            # Buscar en base de datos local
            movie = Movie.query.filter(Movie.title.ilike(title)).first()
            if not movie:
                movie = Movie.query.filter(Movie.title.ilike(f"%{title}%")).first()

            # Si no existe, intentar agregar desde OMDb
            if not movie and omdb_key:
                try:
                    omdb_data = requests.get(f'http://www.omdbapi.com/?t={title}&apikey={omdb_key}').json()
                    if omdb_data.get('Response') == 'True':
                        poster_path = download_poster(omdb_data.get('Poster'))
                        
                        if poster_path:
                            new_movie = Movie(
                                title=omdb_data.get('Title'),
                                description=omdb_data.get('Plot', 'Sin descripción'),
                                poster=poster_path,
                                trailer_url=None
                            )
                            
                            # Asignar géneros
                            genre_mapping = {
                                "Action": "Acción", "Adventure": "Aventura", 
                                "Sci-Fi": "Ciencia Ficción", "Comedy": "Comedia", 
                                "Animation": "Animación", "Fantasy": "Fantasía", 
                                "Horror": "Terror", "Thriller": "Suspenso"
                            }
                            
                            if omdb_data.get('Genre'):
                                for g_raw in omdb_data.get('Genre').split(','):
                                    g_name = g_raw.strip()
                                    g_final = genre_mapping.get(g_name, g_name)
                                    
                                    genre = Genre.query.filter(Genre.name.ilike(g_final)).first()
                                    if not genre:
                                        genre = Genre(name=g_final)
                                        db.session.add(genre)
                                    new_movie.genres.append(genre)
                            
                            db.session.add(new_movie)
                            db.session.commit()
                            movie = new_movie
                            print(f"✅ Agregada: {title}")
                except Exception as ex:
                    print(f"⚠️ Error OMDb: {ex}")

            if movie:
                # Verificar que no fue ya vista
                if current_user.is_authenticated and movie in current_user.seen_list:
                    continue

                g_name = movie.genres[0].name if movie.genres else "Cine"
                processed.append({
                    'id': movie.id,
                    'title': movie.title,
                    'poster': movie.poster,
                    'genres': [g_name],
                    'reason': reason
                })
        return processed

    # Procesar recomendaciones
    top_picks = process_movie_list(raw_data.get('top_picks', []))
    also_like = process_movie_list(raw_data.get('also_like', []))

    if not top_picks and not also_like:
        return jsonify({'error': 'No hay películas nuevas. ¡Buen cinéfilo!'}), 404

    return jsonify({
        'top_picks': top_picks,
        'also_like': also_like
    })

@ai_bp.route('/adventure')
@login_required
def adventure_mode():
    """Página del modo aventura/encuesta"""
    return render_template('ai_concierge.html')