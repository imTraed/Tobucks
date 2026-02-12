"""IA Concierge: recomendaciones de películas con Groq (Catálogo Completo)"""
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
import os
import json
import uuid
import requests
from groq import Groq
from .. import db
from ..models.models import Movie, Genre

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

def download_poster(img_url):
    """Descarga póster si no existe"""
    if not img_url or img_url == 'N/A' or not img_url.startswith('http'): return None
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
    except: return None

@ai_bp.route("/concierge")
@login_required
def concierge():
    return render_template("ai_concierge.html")

@ai_bp.route("/ask_adventure", methods=["POST"])
@login_required
def ask_adventure():
    data = request.json
    narrative = data.get('narrative', '')

    groq_key = current_app.config.get('GROQ_API_KEY') or os.environ.get('GROQ_API_KEY')
    omdb_key = current_app.config.get('OMDB_API_KEY')

    if not groq_key: return jsonify({'error': 'Falta GROQ_API_KEY'}), 500

    # 1. OBTENER CATÁLOGO COMPLETO (Sin límites, como pediste)
    try:
        # Traemos TODOS los títulos de la base de datos
        all_movies = Movie.query.with_entities(Movie.title).all()
        catalog_str = ", ".join([m.title for m in all_movies]) if all_movies else "Vacío."
    except: 
        catalog_str = "No disponible."

    # Historial de vistas (Últimas 50 para mantener contexto relevante)
    seen_str = ""
    if current_user.is_authenticated:
        try:
            seen = [m.title for m in current_user.seen_list][-50:]
            seen_str = ", ".join(seen)
        except: pass

    # 2. Consultar Groq
    try:
        client = Groq(api_key=groq_key)
        
        # Usamos Llama 3 70B para mejor razonamiento con contextos grandes
        chosen_model = "llama-3.3-70b-versatile"

        # Prompt del Sistema
        system_prompt = f"""
        Eres experto en cine.
        CATÁLOGO COMPLETO: [{catalog_str}]
        YA VISTAS: [{seen_str}]
        
        REGLAS:
        1. Contexto "Familia" = CERO contenido adulto.
        2. PRIORIZA SIEMPRE películas del CATÁLOGO LOCAL si encajan.
        3. Si no hay opciones en el catálogo, sugiere clásicos globales.
        4. NO repetir vistas.
        5. Genera 3 "top_picks" y 5 "also_like".
        """

        # Prompt del Usuario
        user_prompt = f"""
        Perfil: "{narrative}"
        
        Responde con este JSON exacto:
        {{
          "top_picks": [
             {{ "title": "Peli 1", "reason": "Breve motivo" }},
             {{ "title": "Peli 2", "reason": "Breve motivo" }},
             {{ "title": "Peli 3", "reason": "Breve motivo" }}
          ],
          "also_like": [
             {{ "title": "Extra 1" }}, {{ "title": "Extra 2" }}, {{ "title": "Extra 3" }}, {{ "title": "Extra 4" }}, {{ "title": "Extra 5" }}
          ]
        }}
        """

        print(f"🚀 Groq ({chosen_model})...")
        
        # Aumentamos max_tokens para asegurar que la respuesta quepa completa
        completion = client.chat.completions.create(
            model=chosen_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5, 
            max_tokens=2048, 
            top_p=1,
            stream=False,
            response_format={"type": "json_object"}
        )

        raw_data = json.loads(completion.choices[0].message.content)

    except Exception as e:
        err = str(e)
        print(f"❌ Error Groq: {err}")
        if "429" in err: return jsonify({'error': '⚠️ IA saturada. Espera 10s.'}), 429
        # Si el error es por contexto muy largo (muchas películas), avisamos
        if "context_length_exceeded" in err: return jsonify({'error': '⚠️ El catálogo es demasiado grande para la IA.'}), 400
        return jsonify({'error': 'Error IA.'}), 500

    # 3. Procesar Resultados
    def process(items):
        res = []
        for item in items:
            title = item.get('title')
            if not title: continue
            
            # Buscar local
            movie = Movie.query.filter(Movie.title.ilike(title)).first()
            if not movie: movie = Movie.query.filter(Movie.title.ilike(f"%{title}%")).first()

            # Importar OMDb si falta (Solo si la IA alucinó algo que no estaba en la lista o si falló el match exacto)
            if not movie and omdb_key:
                try:
                    r = requests.get(f'http://www.omdbapi.com/?t={title}&apikey={omdb_key}', timeout=3).json()
                    if r.get('Response') == 'True':
                        poster = download_poster(r.get('Poster'))
                        movie = Movie(title=r.get('Title'), description=r.get('Plot'), poster=poster)
                        
                        if r.get('Genre'):
                            g_name = r.get('Genre').split(',')[0].strip()
                            g_db = Genre.query.filter(Genre.name.ilike(g_name)).first()
                            if not g_db: 
                                g_db = Genre(name=g_name)
                                db.session.add(g_db)
                            movie.genres.append(g_db)
                        
                        db.session.add(movie)
                        db.session.commit()
                        print(f"✅ Importada: {title}")
                except: pass

            if movie:
                if current_user.is_authenticated and movie in current_user.seen_list: continue
                g_name = movie.genres[0].name if movie.genres else "Cine"
                res.append({
                    'id': movie.id, 'title': movie.title, 
                    'poster': movie.poster, 'genres': [g_name], 
                    'reason': item.get('reason', 'Recomendada')
                })
        return res

    top = process(raw_data.get('top_picks', []))
    also = process(raw_data.get('also_like', []))

    if not top and not also:
        return jsonify({'error': 'Sin resultados.'}), 404

    return jsonify({'top_picks': top, 'also_like': also})