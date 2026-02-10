"""
Rutas de autenticación y gestión de usuarios.
Aquí se maneja el Registro, Login, Logout y las Preferencias.
"""

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# Importamos la base de datos y los modelos necesarios
from .. import db
from ..models.models import User, Genre, UserPreference

# Definimos el Blueprint
users_bp = Blueprint("users", __name__, url_prefix="/users")


# --------------------------------------------------------------------------
# RUTA DE REGISTRO
# --------------------------------------------------------------------------
@users_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Registrar nueva cuenta de usuario.
    GET: Muestra el formulario.
    POST: Procesa los datos y crea el usuario en la DB.
    """
    
    # Si el usuario ya está logueado, lo mandamos al inicio
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        # Obtener datos del formulario
        username = request.form.get("username")
        password = request.form.get("password")
        
        # 1. Validar que los campos no estén vacíos
        if not username or not password:
            flash("Se requieren usuario y contraseña.")
            return render_template("register.html")
        
        # 2. Verificar si el usuario ya existe en la Base de Datos
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash("El nombre de usuario ya está en uso. Intenta con otro.")
            return render_template("register.html")
        
        # 3. Crear el nuevo usuario
        # IMPORTANTE: Nunca guardar contraseñas en texto plano. Usamos generate_password_hash.
        new_user = User(
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        
        # 4. Guardar en la base de datos
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registro exitoso. Por favor inicia sesión.")
            return redirect(url_for("users.login"))
        except Exception as e:
            db.session.rollback() # Si falla, deshacemos cambios
            flash(f"Error al registrar: {str(e)}")

    return render_template("register.html")


# --------------------------------------------------------------------------
# RUTA DE LOGIN (INICIO DE SESIÓN)
# --------------------------------------------------------------------------
@users_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Iniciar sesión.
    GET: Muestra el formulario.
    POST: Valida credenciales e inicia la sesión con Flask-Login.
    """
    
    # Si ya está logueado, no necesita ver el login
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Buscar usuario en la DB
        user = User.query.filter_by(username=username).first()
        
        # Verificar contraseña
        # check_password_hash compara la contraseña escrita con el hash guardado
        if user and check_password_hash(user.password, password):
            login_user(user) # Esto crea la sesión y la cookie
            flash(f"Bienvenido de nuevo, {user.username}!")
            
            # Redirigir a donde quería ir el usuario o al inicio
            next_page = request.args.get('next')
            return redirect(next_page or url_for("main.index"))
        else:
            flash("Usuario o contraseña incorrectos.")
    
    return render_template("login.html")


# --------------------------------------------------------------------------
# RUTA DE LOGOUT (CERRAR SESIÓN)
# --------------------------------------------------------------------------
@users_bp.route("/logout")
@login_required # Solo usuarios logueados pueden cerrar sesión
def logout():
    """Cierra la sesión actual y limpia las cookies."""
    logout_user()
    flash("Has cerrado sesión correctamente.")
    return redirect(url_for("users.login"))


# --------------------------------------------------------------------------
# GESTIÓN DE PREFERENCIAS
# --------------------------------------------------------------------------
@users_bp.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    """
    Permite al usuario seleccionar sus géneros favoritos.
    POST: Recibe una lista de IDs y actualiza la tabla UserPreference.
    """
    
    # Obtener todos los géneros disponibles para mostrarlos en el front
    genres = Genre.query.all()
    
    if request.method == "POST":
        # request.form.getlist permite obtener múltiples checkboxes seleccionados
        selected_genre_ids = request.form.getlist("genres")
        
        try:
            # 1. Limpiar preferencias anteriores (Estrategia: Borrar y Crear)
            # Esto evita duplicados y maneja las des-selecciones fácilmente
            # Nota: Usamos clear() si la relación está configurada en el modelo,
            # si no, habría que hacer un delete query manual. Asumimos relación SQLAlchemy.
            current_user.preferences.clear()
            
            # 2. Agregar las nuevas preferencias seleccionadas
            for gid in selected_genre_ids:
                genre = Genre.query.get(int(gid))
                if genre:
                    # Crear la relación en la tabla intermedia
                    pref = UserPreference(user=current_user, genre=genre)
                    db.session.add(pref)
            
            # 3. Guardar cambios
            db.session.commit()
            
            # Respondemos con JSON porque usualmente estos formularios se envían vía AJAX
            # Si tu formulario es normal, cambia esto por un redirect
            return jsonify({"success": True, "message": "Preferencias guardadas exitosamente."}), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
    
    # GET: Mostrar el formulario
    # Creamos un set con los IDs actuales para marcar los checkboxes en el HTML
    current_genre_ids = {pref.genre_id for pref in current_user.preferences}
    
    return render_template(
        "update_preferences.html",
        genres=genres,
        user_genre_ids=current_genre_ids
    )