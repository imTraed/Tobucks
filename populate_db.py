# Script para llenar base de datos con películas desde API OMDb
import requests
import os
import uuid
import time
from deep_translator import GoogleTranslator
from youtubesearchpython import VideosSearch
from app import create_app, db
from app.models.models import Movie, Genre

# Crear aplicación
app = create_app()

# URL lista de películas
MOVIES_LIST_URL = "https://raw.githubusercontent.com/erik-sytnyk/movies-list/master/db.json"

def get_trailer_url(title):
    """Buscar tráiler en YouTube en español"""
    try:
        query = f"{title} trailer oficial español latino"
        videosSearch = VideosSearch(query, limit=1)
        results = videosSearch.result()
        if results['result']:
            return results['result'][0]['link']
    except:
        pass
    return None

def download_poster(img_url):
    """Descargar y guardar póster localmente"""
    if not img_url or img_url == 'N/A' or not img_url.startswith('http'): 
        return None
    try:
        resp = requests.get(img_url, timeout=10)
        if resp.status_code == 200:
            ext = os.path.splitext(img_url.split('?')[0])[1] or '.jpg'
            if len(ext) > 5: ext = '.jpg'
            filename = f"{uuid.uuid4().hex}{ext}"
            
            base_path = os.path.dirname(os.path.abspath(__file__))
            save_dir = os.path.join(base_path, 'app', 'static', 'uploads')
            os.makedirs(save_dir, exist_ok=True)
            
            with open(os.path.join(save_dir, filename), 'wb') as f:
                f.write(resp.content)
            return f"uploads/{filename}"
    except: 
        return None

def translate_text(text):
    """Traducir sinopsis al español"""
    if not text or text == "N/A": return "Sin descripción."
    try:
        return GoogleTranslator(source='auto', target='es').translate(text)
    except:
        return text

def populate():
    print("\n🎬 Poblando base de datos...")
    
    try:
        response = requests.get(MOVIES_LIST_URL)
        external_data = response.json()
        movies_batch = external_data.get('movies', [])
    except Exception as e:
        print(f"❌ Error descargando lista: {e}")
        return

    omdb_key = app.config.get('OMDB_API_KEY')
    if not omdb_key:
        print("❌ Falta API key de OMDb")
        return

    print(f"🎯 {len(movies_batch)} películas encontradas.\n")

    with app.app_context():
        success_count = 0
        skip_count = 0
        no_poster_count = 0
        
        for i, item in enumerate(movies_batch):
            title = item.get('title')
            
            print(f"[{i+1}/{len(movies_batch)}] {title}...", end="\r")

            # Verificar si ya existe
            if Movie.query.filter(Movie.title.ilike(title)).first():
                skip_count += 1
                continue

            try:
                # Consultar OMDb
                omdb_url = f"http://www.omdbapi.com/?t={title}&apikey={omdb_key}"
                data = requests.get(omdb_url).json()

                if data.get('Response') == 'True':
                    
                    # Descargar póster (debe existir)
                    poster_url = data.get('Poster')
                    poster_path = download_poster(poster_url)

                    if not poster_path:
                        no_poster_count += 1
                        continue 

                    # Traducir y buscar tráiler
                    plot_es = translate_text(data.get('Plot', ''))
                    trailer_link = get_trailer_url(title)

                    # Crear película
                    new_movie = Movie(
                        title=data.get('Title'),
                        description=plot_es,
                        poster=poster_path,
                        trailer_url=trailer_link
                    )

                    # Procesar géneros
                    genre_map = {
                        "Action": "Acción", "Adventure": "Aventura", "Sci-Fi": "Ciencia Ficción",
                        "Comedy": "Comedia", "Fantasy": "Fantasía", "Animation": "Animación",
                        "Family": "Familia", "Mystery": "Misterio", "War": "Guerra",
                        "Thriller": "Suspenso", "Horror": "Terror", "Romance": "Romance",
                        "Crime": "Crimen", "History": "Historia", "Documentary": "Documental"
                    }

                    if data.get('Genre'):
                        for g_raw in data.get('Genre').split(','):
                            g_name = g_raw.strip()
                            final_name = genre_map.get(g_name, g_name)
                            
                            genre_obj = Genre.query.filter(Genre.name.ilike(final_name)).first()
                            if not genre_obj:
                                genre_obj = Genre(name=final_name)
                                db.session.add(genre_obj)
                            new_movie.genres.append(genre_obj)

                    db.session.add(new_movie)
                    db.session.commit()
                    success_count += 1
                    time.sleep(0.2)
                else:
                    no_poster_count += 1
            
            except Exception as e:
                print(f"\n❌ Error con {title}: {e}")

    print("\n" + "="*50)
    print(f"✅ Guardadas: {success_count}")
    print(f"🗑️ Descartadas: {no_poster_count}")
    print(f"⏭️ Existentes: {skip_count}")
    print("="*50)

if __name__ == "__main__":
    populate()
                    success_count += 1
                    time.sleep(0.2) # Breve pausa
                else:
                    # OMDb no encontró la película
                    no_poster_count += 1 # Lo contamos como "no apto"
            
            except Exception as e:
                print(f"\n❌ Error procesando {title}: {e}")

    print("\n" + "="*50)
    print(f"🏁 PROCESO TERMINADO")
    print(f"✅ Guardadas (Con póster y datos): {success_count}")
    print(f"🗑️  Descartadas (Sin póster o no encontradas): {no_poster_count}")
    print(f"⏭️  Saltadas (Ya existían): {skip_count}")
    print("="*50)

if __name__ == "__main__":
    populate()