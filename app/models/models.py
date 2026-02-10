from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_login import UserMixin
from .. import db

# Tabla intermedia: relación película-género (muchos a muchos)
movie_genres = Table(
    "movie_genres",
    db.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)

# Tabla intermedia: relación usuario-película vista (muchos a muchos)
seen_movies = Table(
    "seen_movies",
    db.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True)
)

class Genre(db.Model):
    """Modelo de géneros de películas"""
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    movies = relationship("Movie", secondary=movie_genres, back_populates="genres")
    
    def __repr__(self) -> str:
        return f"<Genre {self.name}>"

class Movie(db.Model):
    """Modelo de películas con información completa"""
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    slug = Column(String(150), unique=True, nullable=True)
    description = Column(Text, nullable=True)
    poster = Column(String(200), nullable=True)
    trailer_url = Column(String(500), nullable=True)
    rating = Column(Float, default=0.0)
    runtime = Column(String(50), nullable=True)

    genres = relationship("Genre", secondary=movie_genres, back_populates="movies", lazy="subquery")

    def __repr__(self) -> str:
        return f"<Movie {self.title}>"

    @property
    def embed_url(self):
        """Convertir URL de YouTube a formato embed para incrustar"""
        if not self.trailer_url:
            return None
        
        url = self.trailer_url.strip()
        
        # Si ya es embed, devolver tal cual
        if "embed/" in url:
            return url
            
        # Formato watch?v= (YouTube desktop)
        if "watch?v=" in url:
            try:
                video_id = url.split("v=")[1].split("&")[0]
                return f"https://www.youtube.com/embed/{video_id}?rel=0&showinfo=0&modestbranding=1"
            except IndexError:
                return None
            
        # Formato youtu.be/ (URL corta)
        if "youtu.be/" in url:
            try:
                video_id = url.split("youtu.be/")[1].split("?")[0]
                return f"https://www.youtube.com/embed/{video_id}?rel=0&showinfo=0&modestbranding=1"
            except IndexError:
                return None
            
        return url

class User(UserMixin, db.Model):
    """Modelo de usuario con autenticación"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)

    # Preferencias de géneros del usuario
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan", lazy="joined")
    
    # Solicitudes de películas del usuario
    requests = relationship("Request", back_populates="user", cascade="all, delete-orphan")

    # Películas vistas por el usuario
    seen_list = relationship("Movie", secondary=seen_movies, backref=db.backref("viewers", lazy="dynamic"), lazy="subquery")

    def __repr__(self) -> str:
        return f"<User {self.username}>"

class UserPreference(db.Model):
    """Modelo de preferencia de usuario (género preferido)"""
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    genre_id = Column(Integer, ForeignKey("genres.id"))
    user = relationship("User", back_populates="preferences")
    genre = relationship("Genre")
    
    def __repr__(self) -> str:
        return f"<UserPreference user={self.user_id} genre={self.genre_id}>"

class Request(db.Model):
    """Modelo de solicitud de película"""
    __tablename__ = 'requests'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    trailer_url = Column(String(300), nullable=True)
    poster = Column(String(300), nullable=True)
    
    status = Column(String(20), default='pending')  # pending, approved, rejected
    created_at = Column(DateTime, default=func.current_timestamp())
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='requests')

    def __repr__(self):
        return f'<Request {self.title}>'