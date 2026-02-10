# Script para probar rutas sin errores
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app import db
import traceback

app = create_app()

with app.app_context():
    client = app.test_client()
    try:
        # Crear usuario de prueba si no existe
        from app.models.models import User
        u = User.query.first()
        if not u:
            from werkzeug.security import generate_password_hash
            u = User(username='debuguser', password=generate_password_hash('debugpass'))
            db.session.add(u)
            db.session.commit()
        
        # Probar ruta de películas
        print('\nProbando /movies/')
        try:
            resp = client.get('/movies/')
            print('Status:', resp.status_code)
        except Exception:
            print('Error en /movies/')
            traceback.print_exc()
        
        # Probar login y preferencias
        print('\nProbando login...')
        try:
            resp_login = client.post('/users/login', 
                data={'username': u.username, 'password': 'debugpass'}, 
                follow_redirects=True)
            print('Login status:', resp_login.status_code)
        except Exception:
            print('Error en login')
            traceback.print_exc()
        
        # Probar preferencias
        print('\nProbando /users/preferences')
        try:
            resp2 = client.get('/users/preferences', follow_redirects=True)
            print('Status:', resp2.status_code)
        except Exception:
            print('Error en preferencias')
            traceback.print_exc()
    except Exception:
        print('Error general')
        traceback.print_exc()
