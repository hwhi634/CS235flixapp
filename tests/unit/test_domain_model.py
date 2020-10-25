from datetime import date

from covid.domain.model import User, Movie, Genre, make_review, make_genre_association, ModelException

import pytest


@pytest.fixture()
def movie():
    return Movie(
        date.fromisoformat('2020-03-15'),
        'test movie',
        'test movie fp',
        'nan',
        'imglink',
        7.6,
        "imagelink",
        None,
        101,
        "jamesbrown",
        ["ben", "dover"],
    )


@pytest.fixture()
def user():
    return User('dbowie', '1234567890')


@pytest.fixture()
def genre():
    return Genre('Mystery')


def test_user_construction(user):
    assert user.username == 'dbowie'
    assert user.password == '1234567890'
    assert repr(user) == '<User dbowie 1234567890>'

    for review in user.reviews:
        # User should have an empty list of Reviews after construction.
        assert False


def test_movie_construction(movie):
    assert movie.id is None
    assert movie.date == date.fromisoformat('2020-03-15')
    assert movie.title == 'test movie'
    assert movie.first_para == 'test movie fp'

    assert movie.number_of_reviews == 0
    assert movie.number_of_genres == 0
    assert repr(
        movie) == '<Movie 2020-03-15 test movie>'


def test_movie_less_than_operator():
    movie_1 = Movie(
        date.fromisoformat('2020-03-15'), "None", "None", "None", "None", 0.0, "None", 0, 0, "None", []
    )

    movie_2 = Movie(
        date.fromisoformat('2020-04-20'), "None", "None", "None", "None", 0.0, "None", 0, 0, "None", []
    )

    assert movie_1 < movie_2


def test_genre_construction(genre):
    assert genre.genre_name == 'Mystery'

    for movie in genre.genreged_movies:
        assert False

    assert not genre.is_applied_to(Movie(date.fromisoformat('2020-04-20'), "None", "None", "None", "None", 0.0, "None", 0, 0, "None", []))


def test_make_review_establishes_relationships(movie, user):
    review_text = 'good film'
    review = make_review(user, movie, review_text, 8)

    # Check that the User object knows about the Review.
    assert review in user.reviews

    # Check that the Review knows about the User.
    assert review.user is user

    # Check that Movie knows about the Review.
    assert review in movie.reviews

    # Check that the Review knows about the Movie.
    assert review.movie is movie


def test_make_genre_associations(movie, genre):
    make_genre_association(movie, genre)

    # Check that the Movie knows about the Genre.
    assert movie.is_genreged()
    assert movie.is_genreged_by(genre)

    # check that the Genre knows about the Movie.
    assert genre.is_applied_to(movie)
    assert movie in genre.genreged_movies


def test_make_genre_associations_with_movie_already_genreged(movie, genre):
    make_genre_association(movie, genre)

    with pytest.raises(ModelException):
        make_genre_association(movie, genre)
