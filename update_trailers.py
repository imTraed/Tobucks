# Script para actualizar tráilers de películas desde YouTube
import time
from app import create_app, db
from app.models.models import Movie
from youtube_search import YoutubeSearch

app = create_app()

def buscar_trailer(titulo):
    """Buscar tráiler en YouTube"""
    try:
        results = YoutubeSearch(f"{titulo} trailer", max_results=1).to_dict()
        if results:
            video_id = results[0]['url_suffix']
            return f"https://www.youtube.com{video_id}"
    except Exception as e:
        print(f"Error: {e}")
    return None

def actualizar_bd():
    print("--- 🎬 Buscando tráilers ---")
    
    with app.app_context():
        movies = Movie.query.all()
        count = 0
        
        for movie in movies:
            # Solo buscar si no tiene tráiler
            if not movie.trailer_url:
                print(f"🔍 {movie.title}...", end="\r")
                
                url = buscar_trailer(movie.title)
                
                if url:
                    movie.trailer_url = url
                    print(f"   ✅ {movie.title}")
                    count += 1
                
                time.sleep(1)
        
        db.session.commit()
        print(f"\n✅ {count} películas actualizadas.")

if __name__ == "__main__":
    actualizar_bd()