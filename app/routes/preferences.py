from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.models import Genre, UserPreference
from .. import db

# Definimos el Blueprint con el nombre 'preferences'
preferences_bp = Blueprint('preferences', __name__, url_prefix='/preferences')

@preferences_bp.route('/update', methods=['GET', 'POST'])
@login_required
def update_preferences():
    # Obtener todos los géneros disponibles para mostrarlos
    genres = Genre.query.all()
    
    # Obtener los IDs de los géneros que el usuario YA tiene seleccionados
    user_genre_ids = [pref.genre_id for pref in current_user.preferences]

    if request.method == 'POST':
        # Obtener lista de IDs seleccionados en el formulario
        selected_genre_ids = request.form.getlist('genres')
        
        # 1. Limpiar preferencias anteriores (Borrar y crear de nuevo es lo más fácil)
        # Ojo: En sistemas grandes es mejor actualizar, pero para este caso está bien.
        for pref in current_user.preferences:
            db.session.delete(pref)
            
        # 2. Guardar las nuevas
        for genre_id in selected_genre_ids:
            new_pref = UserPreference(user_id=current_user.id, genre_id=int(genre_id))
            db.session.add(new_pref)
            
        db.session.commit()
        flash('¡Tus preferencias han sido actualizadas!', 'success')
        
        # Redirigir a las recomendaciones o al inicio
        return redirect(url_for('main.index'))

    return render_template('update_preferences.html', genres=genres, user_genre_ids=user_genre_ids)