# Script para probar generación de grafo de recomendaciones
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.models import User, Genre, Movie, UserPreference
from werkzeug.security import generate_password_hash
import json

app = create_app()

with app.app_context():
    # Crear datos de prueba si no existen
    if Genre.query.count() == 0:
        g = Genre(name='TestGenre')
        db.session.add(g)
        db.session.commit()
    else:
        g = Genre.query.first()

    # Crear película de prueba
    if Movie.query.count() == 0:
        m = Movie(title='TestMovie', description='Desc')
        m.genres.append(g)
        db.session.add(m)
        db.session.commit()
    else:
        m = Movie.query.first()
        if g not in m.genres:
            m.genres.append(g)
            db.session.commit()

    # Crear usuario de prueba
    username = 'testuser'
    password = 'testpass'
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()

    # Agregar preferencia de género
    if not any(pref.genre_id == g.id for pref in user.preferences):
        pref = UserPreference(user=user, genre=g)
        db.session.add(pref)
        db.session.commit()

    # Probar ruta de grafo
    client = app.test_client()
    login_resp = client.post('/users/login', 
        data={'username': username, 'password': password}, 
        follow_redirects=True)
    
    resp = client.get('/recommendations/graph.json')
    print('Status:', resp.status_code)
    
    try:
        data = resp.get_json()
    except:
        data = resp.data.decode('utf-8')
    
    print(json.dumps(data, indent=2, ensure_ascii=False))
