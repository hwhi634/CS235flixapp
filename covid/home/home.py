from flask import Blueprint, render_template, request, jsonify, url_for, redirect, session
import random
import json

from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length

import covid.adapters.repository as repo
import covid.utilities.utilities as utilities
import covid.home.services as services

from covid.authentication.authentication import login_required


home_blueprint = Blueprint(
    'home_bp', __name__)


@home_blueprint.route('/', methods=['GET'])
def home():
    # return redirect("/m?page=0", code=302)
    return render_template('front.html', genre_urls=utilities.get_genres_and_urls())


@home_blueprint.route('/m', methods=['GET'])
def movies_by_genre():
    movies_per_page = 35

    # Read query parameters.
    if 'g' not in request.args:
        genre_name = 'all'
    else:
        genre_name = request.args.get('g')
    s = request.args.get('s')
    if 'page' not in request.args:
        page = 0
    else:
        page = int(request.args.get('page'))
    movie_to_show_reviews = request.args.get('view_reviews_for')

    if movie_to_show_reviews is None:
        # No view-reviews query parameter, so set to a non-existent movie id.
        movie_to_show_reviews = -1
    else:
        # Convert movie_to_show_reviews from string to int.
        movie_to_show_reviews = int(movie_to_show_reviews)

    # if page is None:
    #     # No page query parameter, so initialise page to start at the beginning.
    #     page = 0
    # else:
    #     # Convert page from string to int.
    #     page = int(page)

    # Retrieve movie ids for movies that are genreged with genre_name.
    movie_ids = services.get_movie_ids_for_genre(s, genre_name, repo.repo_instance)
    # print(movie_ids)
    # Retrieve the batch of movies to display on the Web page.

    # print(movie_ids[page+movies_per_page:movies_per_page + movies_per_page])
    # movies = services.get_movies_by_id(movie_ids[page*movies_per_page:movies_per_page + movies_per_page], repo.repo_instance)
    movies = services.get_movies_by_id(movie_ids[page*movies_per_page:page*movies_per_page+movies_per_page], repo.repo_instance)
    # print(movies)
    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if page > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('home_bp.movies_by_genre', s=request.args.get('s'), g=genre_name, page=page - 1, id=request.args.get('id'))
        first_movie_url = url_for('home_bp.movies_by_genre', s=request.args.get('s'), g=genre_name, id=request.args.get('id'))

    if (page+1)*movies_per_page < len(movie_ids):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('home_bp.movies_by_genre', s=request.args.get('s'), g=genre_name, page=page + 1, id=request.args.get('id'))

        last_page = int(len(movie_ids) / movies_per_page)
        if len(movie_ids) % movies_per_page == 0:
            last_page -= movies_per_page
        last_movie_url = url_for('home_bp.movies_by_genre', s=request.args.get('s'), g=genre_name, page=last_page, id=request.args.get('id'))

    # Construct urls for viewing movie reviews and adding reviews.
    for movie in movies:
        movie['view_review_url'] = url_for('home_bp.movies_by_genre', s=request.args.get('s'), g=genre_name, page=page, view_reviews_for=movie['id'])
        movie['add_review_url'] = url_for('home_bp.review_on_movie', movie=movie['id'])
    t = random.randint(1, 1000)
    if 'id' not in request.args:
        choice = services.get_movie_by_id([random.randint(1, 1000)], repo.repo_instance)
    else:
        choice = services.get_movie_by_id([int(request.args.get('id'))], repo.repo_instance)
        t=int(request.args.get('id'))
    choice['add_review_url'] = url_for('home_bp.review_on_movie', movie=t)
    similar=like(choice, services.get_movie_by_id_similar([i for i in range(1000)],repo.repo_instance), 3)
    return render_template(
        'home/home.html',
        genre_urls=utilities.get_genres_and_urls(),
        selected=choice,
        year_urls=utilities.get_year_and_urls(),
        genre=genre_name,
        movies=movies,
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        similar=random.choices(similar, k = 6),
        show_reviews_for_movie=movie_to_show_reviews
    )



@home_blueprint.route('/review', methods=['GET', 'POST'])
@login_required
def review_on_movie():
    # Obtain the username of the currently logged in user.
    username = session['username']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an movie id, when subsequently called with a HTTP POST request, the movie id remains in the
    # form.
    form = ReviewForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the review text has passed data validation.
        # Extract the movie id, representing the reviewed movie, from the form.
        movie_id = int(form.movie_id.data)

        # Use the service layer to store the new review.
        services.add_review(movie_id, form.review.data, username, form.rating.data, repo.repo_instance)

        # Retrieve the movie in dict form.
        movie = services.get_movie(movie_id, repo.repo_instance)

        # Cause the web browser to display the page of all movies that have the same date as the reviewed movie,
        # and display all reviews, including the new review.
        return redirect("/m?id="+str(movie_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the movie id, representing the movie to review, from a query parameter of the GET request.
        movie_id = int(request.args.get('movie'))

        # Store the movie id in the form.
        form.movie_id.data = movie_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the movie id of the movie being reviewed from the form.
        movie_id = int(form.movie_id.data)

    # For a GET or an unsuccessful POST, retrieve the movie to review in dict form, and return a Web page that allows
    # the user to enter a review. The generated Web page includes a form object.
    movie = services.get_movie(movie_id, repo.repo_instance)
    return render_template(
        'home/review_on_movie.html',
        title='Edit movie',
        movie=movie,
        form=form,
        handler_url=url_for('home_bp.review_on_movie'),
        genre_urls=utilities.get_genres_and_urls()
    )


def like(c, l, q):
    d = []
    for i in l:
        if i not in d and c["id"] != i["id"]:
            for f in [v['name'] for v in c["genres"]]:
                if f in [e['name'] for e in i["genres"]]:
                    if c["director"] == i["director"]:
                        d.insert(0, i)
                        break
                    else:
                        d.append(i)
                        break
    return d if len(d) > 0 else []


class ReviewForm(FlaskForm):
    review = TextAreaField('Review', [
        DataRequired(),
        Length(min=4, message='Your review is too short')])
    rating = SelectField('Rating', [DataRequired()], choices=[(i, i) for i in range(1,11)])
    movie_id = HiddenField("Movie id")
    submit = SubmitField('Submit')