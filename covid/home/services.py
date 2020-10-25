from typing import List, Iterable

from covid.adapters.repository import AbstractRepository
from covid.domain.model import make_review, Movie, Review, Genre
from datetime import date, datetime

class NonExistentMovieException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_review(movie_id: int, review_text: str, username: str, rating, repo: AbstractRepository):
    # Check that the movie exists.
    movie = repo.get_movie(movie_id)
    if movie is None:
        raise NonExistentMovieException

    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    # Create review.
    print(movie)
    review = make_review(user, movie, review_text, rating)

    # Update the repository.
    repo.add_review(review)


def get_movie(movie_id: int, repo: AbstractRepository):
    movie = repo.get_movie(movie_id)

    if movie is None:
        raise NonExistentMovieException

    return movie_to_dict(movie)


def get_first_movie(repo: AbstractRepository):

    movie = repo.get_first_movie()

    return movie_to_dict(movie)


def get_last_movie(repo: AbstractRepository):

    movie = repo.get_last_movie()
    return movie_to_dict(movie)


def get_movies_by_date(date, repo: AbstractRepository):
    # Returns movies for the target date (empty if no matches), the date of the previous movie (might be null), the date of the next movie (might be null)

    movies = repo.get_movies_by_date(target_date=date)

    movies_dto = list()
    prev_date = next_date = None

    if len(movies) > 0:
        prev_date = repo.get_date_of_previous_movie(movies[0])
        next_date = repo.get_date_of_next_movie(movies[0])

        # Convert Movies to dictionary form.
        movies_dto = movies_to_dict(movies)

    return movies_dto, prev_date, next_date


def get_movie_ids_for_genre(s, genre_name, repo: AbstractRepository):
    movie_ids = repo.get_movie_ids_for_genre(s, genre_name)

    return movie_ids


def get_movies_by_id(id_list, repo: AbstractRepository):
    movies = repo.get_movies_by_id(id_list)

    # Convert Movies to dictionary form.
    movies_as_dict = movies_to_dict(movies)
    return movies_as_dict


def get_movie_by_id(id_list, repo: AbstractRepository):
    movies = repo.get_movies_by_id(id_list)

    return movie_to_dict(movies[0])


def get_movie_by_id_similar(id_list, repo: AbstractRepository):
    movies = repo.get_movies_by_id(id_list)

    return [movie_to_dict_sim(movie) for movie in movies]

def get_reviews_for_movie(movie_id, repo: AbstractRepository):
    movie = repo.get_movie(movie_id)

    if movie is None:
        raise NonExistentMovieException

    return reviews_to_dict(movie.reviews)


# ============================================
# Functions to convert model entities to dicts
# ============================================
def moviepage_to_dict(movie: Movie):
    movie_dict = {
        'id': movie.id,
        'title': movie.title,
        'image_hyperlink': movie.image_hyperlink
    }
    return movie_dict


def movie_to_dict(movie: Movie):
    print(movie)
    movie_dict = {
        'id': movie.id,
        'date': movie.date.year,
        'title': movie.title,
        'first_para': movie.first_para,
        'image_hyperlink': movie.image_hyperlink,
        'back_hyperlink': movie.back_hyperlink,
        'reviews': reviews_to_dict(movie.reviews),
        'genres': genres_to_dict(movie.genres),
        'runtime': movie.runtime,
        'rating': movie.rating,
        'director': movie.director,
        'actors': movie.actors
    }
    return movie_dict


def movie_to_dict_sim(movie: Movie):
    movie_dict = {
        'id': movie.id,
        'title': movie.title,
        'genres': genres_to_dict(movie.genres),
        'director': movie.director,
        'image_hyperlink': movie.image_hyperlink
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [moviepage_to_dict(movie) for movie in movies]


def review_to_dict(review: Review):
    review_dict = {
        'username': review.user.username,
        'movie_id': review.movie.id,
        'review_text': review.review,
        'timestamp': review.timestamp,
        'rating': review.rating
    }
    return review_dict


def reviews_to_dict(reviews: Iterable[Review]):
    return [review_to_dict(review) for review in reviews]


def genre_to_dict(genre: Genre):
    genre_dict = {
        'name': genre.genre_name
        # 'genreged_movies': [movie.id for movie in genre.genreged_movies]
    }
    return genre_dict


def genres_to_dict(genres: Iterable[Genre]):
    return [genre_to_dict(genre) for genre in genres]


# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_movie(dict):
    movie = Movie(dict.id, dict.date, dict.title, dict.first_para, dict.hyperlink)
    # Note there's no reviews or genres.
    return movie
