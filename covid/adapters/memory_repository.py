import csv
import os
from datetime import date, datetime
from typing import List
from fuzzywuzzy import fuzz
from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash

from covid.adapters.repository import AbstractRepository, RepositoryException
from covid.domain.model import Movie, Genre, User, Review, make_genre_association, make_review


class MemoryRepository(AbstractRepository):
    # Movies ordered by date, not id. id is assumed unique.

    def __init__(self):
        self._movies = list()
        self._movies_index = dict()
        self._genres = list()
        self._users = list()
        self._reviews = list()

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username), None)

    def add_movie(self, movie: Movie):
        insort_left(self._movies, movie)
        self._movies_index[movie.id] = movie

    def get_movie(self, id: int) -> Movie:
        movie = None

        try:
            movie = self._movies_index[id]
        except KeyError:
            pass  # Ignore exception and return None.

        return movie

    def get_movies_by_date(self, target_date: date) -> List[Movie]:
        target_movie = Movie(
            date=target_date,
            title=None,
            first_para=None,
            hyperlink=None,
            image_hyperlink=None,
            rating=None
        )
        matching_movies = list()

        try:
            index = self.movie_index(target_movie)
            for movie in self._movies[index:None]:
                if movie.date == target_date:
                    matching_movies.append(movie)
                else:
                    break
        except ValueError:
            # No movies for specified date. Simply return an empty list.
            pass

        # return matching_movies
        return self._movies

    def get_number_of_movies(self):
        return len(self._movies)

    def get_first_movie(self):
        movie = None

        if len(self._movies) > 0:
            movie = self._movies[0]
        return movie

    def get_last_movie(self):
        movie = None

        if len(self._movies) > 0:
            movie = self._movies[-1]
        return movie

    def get_movies_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent Movie ids in the repository.
        existing_ids = [id for id in id_list if id in self._movies_index]

        # Fetch the Movies.
        movies = [self._movies_index[id] for id in existing_ids]
        return movies

    def get_movie_ids_for_genre(self, s: str, genre_name: str):
        # Linear search, to find the first occurrence of a Genre with the name genre_name.
        # genre = next((genre for genre in self._genres if genre.genre_name == genre_name), None)
        d = []
        # Retrieve the ids of movies associated with the Genre.
        print(genre_name)
        if s is not None:
            for i in self._movies:
                if genre_name == 'all':
                    if fuzz.partial_ratio(s, i.title) > 70:
                        d.append(i.id)
                else:
                    if fuzz.partial_ratio(s, i.title)>70 and genre_name in [i.genre_name for i in list(i.genres)]:
                        d.append(i.id)
            return d
        if genre_name != 'all':
            for i in self._movies:
                if genre_name in [i.genre_name for i in list(i.genres)]:
                    d.append(i.id)
            return d
        if len(self._movies_index) > 0:
            return list(self._movies_index.keys())
        else:
            # No Genre with name genre_name, so return an empty list.
            return list()

    def get_date_of_previous_movie(self, movie: Movie):
        previous_date = None

        try:
            index = self.movie_index(movie)
            for stored_movie in reversed(self._movies[0:index]):
                if stored_movie.date < movie.date:
                    previous_date = stored_movie.date
                    break
        except ValueError:
            # No earlier movies, so return None.
            pass

        return previous_date

    def get_date_of_next_movie(self, movie: Movie):
        next_date = None

        try:
            index = self.movie_index(movie)
            for stored_movie in self._movies[index + 1:len(self._movies)]:
                if stored_movie.date > movie.date:
                    next_date = stored_movie.date
                    break
        except ValueError:
            # No subsequent movies, so return None.
            pass

        return next_date

    def add_genre(self, genre: Genre):
        self._genres.append(genre)

    def get_genres(self) -> List[Genre]:
        return self._genres

    def add_review(self, review: Review):
        super().add_review(review)
        self._reviews.append(review)

    def get_movie(self, rank):
        existing_ids = [rank]
        return self.get_movies_by_id([rank])[0]

    def get_reviews(self):
        return self._reviews

    # Helper method to return movie index.
    def movie_index(self, movie: Movie):
        index = bisect_left(self._movies, movie)
        if index != len(self._movies) and self._movies[index].date == movie.date:
            return index
        raise ValueError


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_movies_and_genres(data_path: str, repo: MemoryRepository):
    genres = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'Data1000Movies.csv')):

        movie_key = int(data_row[0])
        movie_genres = data_row[2].split(",")
        # Add any new genres; associate the current movie with genres.
        for genre in movie_genres:
            if genre not in genres.keys():
                genres[genre] = list()
            genres[genre].append(movie_key)

        # Create Movie object.
        movie = Movie(
            date=date.fromisoformat(data_row[12]),
            title=data_row[1],
            first_para=data_row[3],
            hyperlink="nan",
            image_hyperlink=data_row[14],
            id=movie_key,
            rating=data_row[8],
            back_hyperlink=data_row[13],
            runtime=int(data_row[7]),
            director=data_row[4],
            actors=data_row[5].split(",")
        )

        # Add the Movie to the repository.
        repo.add_movie(movie)

    # Create Genre objects, associate them with Movies and add them to the repository.
    for genre_name in genres.keys():
        genre = Genre(genre_name)
        for movie_id in genres[genre_name]:
            movie = repo.get_movie(movie_id)
            make_genre_association(movie, genre)
        repo.add_genre(genre)


def load_users(data_path: str, repo: MemoryRepository):
    users = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'users.csv')):
        user = User(
            username=data_row[1],
            password=generate_password_hash(data_row[2])
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_reviews(data_path: str, repo: MemoryRepository, users):
    for data_row in read_csv_file(os.path.join(data_path, 'comments.csv')):
        review = make_review(
            review_text=data_row[3],
            user=users[data_row[1]],
            movie=repo.get_movie(int(data_row[2])),
            rating=int(data_row[5])
        )
        repo.add_review(review)


def populate(data_path: str, repo: MemoryRepository):
    # Load movies and genres into the repository.
    load_movies_and_genres(data_path, repo)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load reviews into the repository.
    print(os.path.join(data_path, 'comments.csv'))
    load_reviews(data_path, repo, users)
