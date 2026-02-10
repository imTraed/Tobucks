# Script para limpiar y normalizar géneros a español
from app import create_app, db
from app.models.models import Genre, Movie, UserPreference

app = create_app()

# Mapeo de géneros inglés a español
GENRE_MAPPING = {
    "Action": "Acción",
    "Adventure": "Aventura",
    "Sci-Fi": "Ciencia Ficción",
    "Comedy": "Comedia",
    "Fantasy": "Fantasía",
    "Animation": "Animación",
    "Drama": "Drama",
    "Horror": "Terror",
    "Thriller": "Suspenso",
    "Romance": "Romance",
    "Mystery": "Misterio",
    "Crime": "Crimen",
    "Documentary": "Documental",
    "History": "Historia",
    "War": "Guerra",
    "Family": "Familia",
    "Music": "Música",
    "Musical": "Música",
    "Western": "Western",
    "Biography": "Biografía",
    "Sport": "Deportes",
    "Short": "Cortometraje",
    "Film-Noir": "Cine Negro",
    "Adult": "Adultos"
}

def clean_genres():
    print("🧹 Limpiando géneros...")
    
    with app.app_context():
        # Crear géneros en español
        print("--- Creando géneros en español ---")
        spanish_genres = {}
        
        for bad, good in GENRE_MAPPING.items():
            # Buscar si existe género bueno
            g_good = Genre.query.filter(Genre.name.ilike(good)).first()
            if not g_good:
                g_good = Genre(name=good)
                db.session.add(g_good)
                db.session.commit()
                print(f"✅ Creado: {good}")
            spanish_genres[good] = g_good

        # Migrar películas y eliminar duplicados
        print("\n--- Migrando películas ---")
        for bad, good in GENRE_MAPPING.items():
            if bad == good:
                continue

            # Buscar género malo
            g_bad = Genre.query.filter(Genre.name.ilike(bad)).first()
            g_good = spanish_genres[good]

            if g_bad and g_bad.id != g_good.id:
                print(f"🔄 {bad} -> {good}...")
                
                # Mover películas
                count_movies = 0
                for movie in g_bad.movies:
                    if g_good not in movie.genres:
                        movie.genres.append(g_good)
                        count_movies += 1
                
                # Mover preferencias de usuario
                try:
                    prefs = UserPreference.query.filter_by(genre_id=g_bad.id).all()
                    for p in prefs:
                        # Verificar si ya existe
                        exists = UserPreference.query.filter_by(user_id=p.user_id, genre_id=g_good.id).first()
                        if not exists:
                            p.genre_id = g_good.id
                        else:
                            db.session.delete(p)
                except:
                    pass

                # Eliminar género malo
                db.session.delete(g_bad)
                db.session.commit()
                print(f"   ✨ {count_movies} películas migradas.")
            
        print("\n✅ Limpieza completada.")

if __name__ == "__main__":
    clean_genres()