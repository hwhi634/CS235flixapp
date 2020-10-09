from flask import Blueprint, render_template, request, jsonify
import random
import covid.utilities.utilities as utilities
from datetime import date, datetime
import requests


home_blueprint = Blueprint(
    'home_bp', __name__)


@home_blueprint.route('/movie_select')
def movieselect():
    a = utilities.get_movie(request.args.get('id', 0, type=int))
    return jsonify(a)


@home_blueprint.route('/movie')
def movieid():
    sa = utilities.get_selected_articles(1000)
    a = utilities.get_movie(request.args.get('id', 0, type=int))
    return render_template(
        'home/home.html',
        selected_articles=sa,
        tag_urls=utilities.get_tags_and_urls(),
        random=a,
        year_urls=utilities.get_year_and_urls()
    )


@home_blueprint.route('/', methods=['GET'])
def home():
    sa = utilities.get_selected_articles(1000)
    return render_template(
        'home/home.html',
        selected_articles=sa,
        tag_urls=utilities.get_tags_and_urls(),
        random=random.choice(sa),
        year_urls=utilities.get_year_and_urls()
    )
