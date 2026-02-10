"""Rutas para gestión de géneros de películas"""

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
)
from flask_login import login_required

from .. import db
from ..models.models import Genre

genres_bp = Blueprint("genres", __name__, url_prefix="/genres")

@genres_bp.route("/", defaults={"page": 1})
@genres_bp.route("/<int:page>")
@login_required
def list_genres(page):
    """Listar todos los géneros con paginación"""
    per_page = 10
    genres = Genre.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        "genres.html",
        genres=genres.items,
        current_page=page,
        total_pages=genres.pages
    )

@genres_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_genre():
    """Agregar nuevo género"""
    if request.method == "POST":
        name = request.form.get("name")
        
        if not name:
            flash("El nombre es requerido.")
            return render_template("add_genre.html")
        
        # Verificar que no existe
        if Genre.query.filter_by(name=name).first():
            flash("El género ya existe.")
            return render_template("add_genre.html")
        
        # Crear y guardar
        genre = Genre(name=name)
        db.session.add(genre)
        db.session.commit()
        
        flash("Género creado.")
        return redirect(url_for("genres.list_genres"))
    
    return render_template("add_genre.html")

@genres_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_genre(id):
    """Editar género existente"""
    genre = Genre.query.get(id)
    
    if not genre:
        flash("Género no encontrado.")
        return redirect(url_for("genres.list_genres"))
    
    if request.method == "POST":
        name = request.form.get("name")
        
        if not name:
            flash("El nombre es requerido.")
            return render_template("edit_genre.html", genre=genre)
        
        # Verificar duplicado
        if Genre.query.filter(Genre.name == name, Genre.id != id).first():
            flash("El nombre ya existe.")
            return render_template("edit_genre.html", genre=genre)
        
        genre.name = name
        db.session.commit()
        
        flash("Género actualizado.")
        return redirect(url_for("genres.list_genres"))
    
    return render_template("edit_genre.html", genre=genre)

@genres_bp.route("/delete/<int:id>")
@login_required
def delete_genre(id):
    """Eliminar género"""
    genre = Genre.query.get(id)
    
    if genre:
        db.session.delete(genre)
        db.session.commit()
        flash("Género eliminado.")
    
    return redirect(url_for("genres.list_genres"))
        
        # Agregar el nuevo género a la sesión de la base de datos
        db.session.add(genre)
        
        # Confirmar los cambios en la base de datos
        db.session.commit()
        
        # Mostrar un mensaje de éxito al usuario
        flash("Género añadido correctamente.")
        
        # Redirigir a la lista de géneros
        return redirect(url_for("genres.list_genres"))
    
    # Si es GET, simplemente mostrar el formulario vacío
    return render_template("add_genre.html")


# Ruta para editar un género existente
# <int:genre_id> es un parámetro dinámico que captura el ID del género
# methods=["GET", "POST"] permite tanto mostrar el formulario como procesarlo
@genres_bp.route("/edit/<int:genre_id>", methods=["GET", "POST"])
# @login_required asegura que solo usuarios autenticados pueden acceder
@login_required
def edit_genre(genre_id: int):
    """
    Maneja tanto la visualización del formulario de edición (GET) como la actualización (POST).
    
    GET: Muestra el formulario con el nombre actual del género
    POST: Procesa el envío del formulario y actualiza el género
    
    Args:
        genre_id (int): ID del género a editar
    
    Returns:
        GET: HTML del formulario de edición
        POST: Redirección a la lista de géneros si es exitoso, o vuelve al formulario si hay error
    """
    
    # Obtener el género por su ID, o mostrar error 404 si no existe
    # get_or_404 busca el registro y genera un error 404 automáticamente
    genre = Genre.query.get_or_404(genre_id)
    
    # Comprobar si es una solicitud POST (envío del formulario)
    if request.method == "POST":
        # Obtener el nuevo nombre del género del formulario
        name = request.form.get("name")
        
        # Validar que el nombre no esté vacío
        if not name:
            # Mostrar un mensaje de error al usuario
            flash("El nombre del género no puede estar vacío.")
            # Volver a mostrar el formulario con los datos actuales
            return render_template("edit_genre.html", genre=genre)
        
        # Actualizar el nombre del género
        genre.name = name
        
        # Confirmar los cambios en la base de datos
        db.session.commit()
        
        # Mostrar un mensaje de éxito al usuario
        flash("Género actualizado correctamente.")
        
        # Redirigir a la lista de géneros
        return redirect(url_for("genres.list_genres"))
    
    # Si es GET, mostrar el formulario con los datos actuales
    return render_template("edit_genre.html", genre=genre)


# Ruta para eliminar un género
# <int:genre_id> es un parámetro dinámico que captura el ID del género
# methods=["POST"] solo acepta solicitudes POST por seguridad
@genres_bp.route("/delete/<int:genre_id>", methods=["POST"])
# @login_required asegura que solo usuarios autenticados pueden acceder
@login_required
def delete_genre(genre_id: int):
    """
    Elimina un género de la base de datos.
    
    Solo acepta solicitudes POST para evitar eliminaciones accidentales por GET.
    
    Args:
        genre_id (int): ID del género a eliminar
    
    Returns:
        Redirección a la lista de géneros
    """
    
    # Obtener el género por su ID, o mostrar error 404 si no existe
    # get_or_404 busca el registro y genera un error 404 automáticamente
    genre = Genre.query.get_or_404(genre_id)
    
    # Eliminar el género de la sesión de la base de datos
    # Las películas asociadas pueden también eliminarse según la cascada configurada
    db.session.delete(genre)
    
    # Confirmar los cambios en la base de datos
    db.session.commit()
    
    # Mostrar un mensaje de éxito al usuario
    flash("Género eliminado correctamente.")
    
    # Redirigir a la lista de géneros
    return redirect(url_for("genres.list_genres"))