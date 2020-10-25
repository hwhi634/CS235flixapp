from datetime import date, datetime
from typing import List, Iterable


class User:
    def __init__(
            self, username: str, password: str
    ):
        self._username: str = username
        self._password: str = password
        self._reviews: List[Review] = list()

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    @property
    def reviews(self) -> Iterable['Review']:
        return iter(self._reviews)

    def add_review(self, review: 'Review'):
        self._reviews.append(review)

    def __repr__(self) -> str:
        return f'<User {self._username} {self._password}>'

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return other._username == self._username


class Review:
    def __init__(
            self, user: User, movie: 'Movie', review: str, rating: int):
        self._user: User = user
        self._movie: Movie = movie
        self._review: Review = review
        self._timestamp: datetime = datetime.now()
        self._rating = rating

    @property
    def user(self) -> User:
        return self._user

    @property
    def rating(self) -> int:
        return self._rating

    @property
    def movie(self) -> 'Movie':
        return self._movie

    @property
    def review(self) -> str:
        return self._review

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    def __eq__(self, other):
        if not isinstance(other, Review):
            return False
        return other._user == self._user and other._movie == self._movie and other._review == self._review and other._timestamp == self._timestamp


class Movie:
    def __init__(self, date: date, title: str, first_para: str, hyperlink: str, image_hyperlink: str, rating: float, back_hyperlink:str, id:int, runtime: int, director:str, actors:list):
        self._id: int = id
        self._date: date = date
        self._title: str = title
        self._first_para: str = first_para
        self._hyperlink: str = hyperlink
        self._image_hyperlink: str = image_hyperlink
        self._reviews: List[Review] = list()
        self._genres: List[Genre] = list()
        self._rating: float = rating
        self._back_hyperlink: str = back_hyperlink
        self._runtime: int = runtime
        self._director: str = director
        self._actors: list = actors

    @property
    def id(self) -> int:
        return self._id

    @property
    def director(self) -> str:
        return self._director

    @property
    def actors(self) -> list:
        return self._actors

    @property
    def rating(self) -> float:
        return self._rating

    @property
    def runtime(self) -> int:
        return self._runtime

    @property
    def date(self) -> date:
        return self._date

    @property
    def title(self) -> str:
        return self._title

    @property
    def first_para(self) -> str:
        return self._first_para

    @property
    def hyperlink(self) -> str:
        return self._hyperlink

    @property
    def back_hyperlink(self) -> str:
        return self._back_hyperlink

    @property
    def image_hyperlink(self) -> str:
        return self._image_hyperlink

    @property
    def reviews(self) -> Iterable[Review]:
        return iter(self._reviews)

    @property
    def number_of_reviews(self) -> int:
        return len(self._reviews)

    @property
    def number_of_genres(self) -> int:
        return len(self._genres)

    @property
    def genres(self) -> Iterable['Genre']:
        return iter(self._genres)

    def is_genreged_by(self, genre: 'Genre'):
        return genre in self._genres

    def is_genreged(self) -> bool:
        return len(self._genres) > 0

    def add_review(self, review: Review):
        self._reviews.append(review)

    def add_genre(self, genre: 'Genre'):
        self._genres.append(genre)

    def __repr__(self):
        return f'<Movie {self._date.isoformat()} {self._title}>'

    def __eq__(self, other):
        if not isinstance(other, Movie):
            return False
        return (
                other._date == self._date and
                other._title == self._title and
                other._first_para == self._first_para and
                other._hyperlink == self._hyperlink and
                other._image_hyperlink == self._image_hyperlink
        )

    def __lt__(self, other):
        return self._date < other._date


class Genre:
    def __init__(
            self, genre_name: str
    ):
        self._genre_name: str = genre_name
        self._genreged_movies: List[Movie] = list()

    @property
    def genre_name(self) -> str:
        return self._genre_name

    @property
    def genreged_movies(self) -> Iterable[Movie]:
        return iter(self._genreged_movies)

    @property
    def number_of_genreged_movies(self) -> int:
        return len(self._genreged_movies)

    def is_applied_to(self, movie: Movie) -> bool:
        return movie in self._genreged_movies

    def add_movie(self, movie: Movie):
        self._genreged_movies.append(movie)

    def __eq__(self, other):
        if not isinstance(other, Genre):
            return False
        return other._genre_name == self._genre_name


class ModelException(Exception):
    pass


def make_review(user, movie, review_text, rating):
    review = Review(user, movie, review_text, rating)
    user.add_review(review)
    movie.add_review(review)

    return review


def make_genre_association(movie: Movie, genre: Genre):
    if genre.is_applied_to(movie):
        raise ModelException(f'Genre {genre.genre_name} already applied to Movie "{movie.title}"')

    movie.add_genre(genre)
    genre.add_movie(movie)
