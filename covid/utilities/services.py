from typing import Iterable
import random
import json
import urllib.parse
from datetime import date, datetime

from covid.adapters.repository import AbstractRepository
from covid.domain.model import Movie


def get_movie(rank, repo: AbstractRepository):
    movie = repo.get_movie(rank)
    print(movie)
    return movie_to_dict(movie)


def get_genre_names(repo: AbstractRepository):
    genres = repo.get_genres()
    genre_names = [genre.genre_name for genre in genres]

    return genre_names


def get_years(repo: AbstractRepository):
    genres = repo.get_genres()
    genre_names = [genre.genre_name for genre in genres]

    return genre_names


def get_random_movies(quantity, repo: AbstractRepository):
    movie_count = repo.get_number_of_movies()

    if quantity >= movie_count:
        # Reduce the quantity of ids to generate if the repository has an insufficient number of movies.
        quantity = movie_count - 1

    # Pick distinct and random movies.
    random_ids = range(1, movie_count)
    movies = repo.get_movies_by_id(random_ids)

    return movies_to_dict(movies)


# ============================================
# Functions to convert dicts to model entities
# ============================================

def movie_to_dict(movie: Movie):
    movie_dict = {
        'date': movie.date,
        'title': movie.title,
        'image_hyperlink': movie.image_hyperlink,
        'back_hyperlink': movie.back_hyperlink,
        'fp': movie.first_para,
        'id': movie.id,
        'runtime': movie.runtime,
        'rating': movie.rating
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [movie_to_dict(movie) for movie in movies]
