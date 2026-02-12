from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from ..models.models import Genre, UserPreference
from .. import db

# Definimos el Blueprint
preferences_bp = Blueprint('preferences', __name__, url_prefix='/preferences')

@preferences_bp.route('/update', methods=['GET', 'POST'])
@login_required
def update_preferences():
    # Ordenar alfabéticamente
    genres = Genre.query.order_by(Genre.name.asc()).all()
    user_genre_ids = [pref.genre_id for pref in current_user.preferences]

    if request.method == 'POST':
        selected_genre_ids = request.form.getlist('genres')
        
        # 1. Borrar preferencias viejas
        UserPreference.query.filter_by(user_id=current_user.id).delete()
            
        # 2. Guardar nuevas
        for genre_id in selected_genre_ids:
            new_pref = UserPreference(user_id=current_user.id, genre_id=int(genre_id))
            db.session.add(new_pref)
            
        db.session.commit()
        
        # Soporte AJAX para el botón flotante
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
            
        flash('¡Tus preferencias han sido actualizadas!', 'success')
        return redirect(url_for('main.index'))

    # Usamos tu nombre de archivo original: update_preferences.html
    return render_template('update_preferences.html', genres=genres, user_genre_ids=user_genre_ids)

# --- FUNCIÓN DE BORRADO (ADMIN) ---
@preferences_bp.route('/delete_genre/<int:genre_id>', methods=['POST'])
@login_required
def delete_genre(genre_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'msg': 'No autorizado'}), 403
    
    try:
        genre = Genre.query.get_or_404(genre_id)
        
        # Primero limpiar referencias para evitar error de llave foránea
        UserPreference.query.filter_by(genre_id=genre.id).delete()
        
        # Luego borrar el género
        db.session.delete(genre)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'msg': str(e)}), 500