"""
Utilidades para construir grafos de películas y géneros.

Funciones para crear un grafo bipartito donde películas y géneros
son nodos y las aristas conectan películas con sus géneros.
"""

import networkx as nx

from ..models.models import Movie, Genre


def build_movie_genre_graph() -> nx.Graph:
    """Construir grafo bipartito de películas y géneros.

    Nodos contienen atributo 'type' (movie o genre).
    Aristas conectan una película con cada uno de sus géneros.

    Returns:
        Grafo de NetworkX
    """
    G = nx.Graph()
    
    # Agregar nodos de géneros
    for genre in Genre.query.all():
        G.add_node(f"g{genre.id}", label=genre.name, type="genre")
    
    # Agregar nodos de películas y aristas a géneros
    for movie in Movie.query.all():
        movie_node = f"m{movie.id}"
        G.add_node(movie_node, label=movie.title, type="movie")
        for genre in movie.genres:
            genre_node = f"g{genre.id}"
            G.add_edge(movie_node, genre_node)
    
    return G