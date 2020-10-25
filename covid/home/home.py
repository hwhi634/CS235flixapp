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
    return render_template('front.html', tag_urls=utilities.get_tags_and_urls())


@home_blueprint.route('/m', methods=['GET'])
def articles_by_tag():
    articles_per_page = 35

    # Read query parameters.
    if 'g' not in request.args:
        tag_name = 'all'
    else:
        tag_name = request.args.get('g')
    s = request.args.get('s')
    if 'page' not in request.args:
        page = 0
    else:
        page = int(request.args.get('page'))
    article_to_show_comments = request.args.get('view_comments_for')

    if article_to_show_comments is None:
        # No view-comments query parameter, so set to a non-existent article id.
        article_to_show_comments = -1
    else:
        # Convert article_to_show_comments from string to int.
        article_to_show_comments = int(article_to_show_comments)

    # if page is None:
    #     # No page query parameter, so initialise page to start at the beginning.
    #     page = 0
    # else:
    #     # Convert page from string to int.
    #     page = int(page)

    # Retrieve article ids for articles that are tagged with tag_name.
    article_ids = services.get_article_ids_for_tag(s, tag_name, repo.repo_instance)
    # print(article_ids)
    # Retrieve the batch of articles to display on the Web page.

    # print(article_ids[page+articles_per_page:articles_per_page + articles_per_page])
    # articles = services.get_articles_by_id(article_ids[page*articles_per_page:articles_per_page + articles_per_page], repo.repo_instance)
    articles = services.get_articles_by_id(article_ids[page*articles_per_page:page*articles_per_page+articles_per_page], repo.repo_instance)
    # print(articles)
    first_article_url = None
    last_article_url = None
    next_article_url = None
    prev_article_url = None

    if page > 0:
        # There are preceding articles, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_article_url = url_for('home_bp.articles_by_tag', s=request.args.get('s'), g=tag_name, page=page - 1, id=request.args.get('id'))
        first_article_url = url_for('home_bp.articles_by_tag', s=request.args.get('s'), g=tag_name, id=request.args.get('id'))

    if (page+1)*articles_per_page < len(article_ids):
        # There are further articles, so generate URLs for the 'next' and 'last' navigation buttons.
        next_article_url = url_for('home_bp.articles_by_tag', s=request.args.get('s'), g=tag_name, page=page + 1, id=request.args.get('id'))

        last_page = int(len(article_ids) / articles_per_page)
        if len(article_ids) % articles_per_page == 0:
            last_page -= articles_per_page
        last_article_url = url_for('home_bp.articles_by_tag', s=request.args.get('s'), g=tag_name, page=last_page, id=request.args.get('id'))

    # Construct urls for viewing article comments and adding comments.
    for article in articles:
        article['view_comment_url'] = url_for('home_bp.articles_by_tag', s=request.args.get('s'), g=tag_name, page=page, view_comments_for=article['id'])
        article['add_comment_url'] = url_for('home_bp.comment_on_article', article=article['id'])
    t = random.randint(1, 1000)
    if 'id' not in request.args:
        t=[random.randint(1, 1000)]
        choice = services.get_article_by_id(t, repo.repo_instance)
    else:
        choice = services.get_article_by_id([int(request.args.get('id'))], repo.repo_instance)
        t=int(request.args.get('id'))
    choice['add_comment_url'] = url_for('home_bp.comment_on_article', article=t)
    similar=like(choice, services.get_article_by_id_similar([i for i in range(1000)],repo.repo_instance), 3)
    return render_template(
        'home/home.html',
        tag_urls=utilities.get_tags_and_urls(),
        selected=choice,
        year_urls=utilities.get_year_and_urls(),
        genre=tag_name,
        articles=articles,
        first_article_url=first_article_url,
        last_article_url=last_article_url,
        prev_article_url=prev_article_url,
        next_article_url=next_article_url,
        similar=random.choices(similar, k = 6),
        show_comments_for_article=article_to_show_comments
    )



@home_blueprint.route('/comment', methods=['GET', 'POST'])
@login_required
def comment_on_article():
    # Obtain the username of the currently logged in user.
    username = session['username']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with an article id, when subsequently called with a HTTP POST request, the article id remains in the
    # form.
    form = CommentForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the comment text has passed data validation.
        # Extract the article id, representing the commented article, from the form.
        article_id = int(form.article_id.data)

        # Use the service layer to store the new comment.
        services.add_comment(article_id, form.comment.data, username, form.rating.data, repo.repo_instance)

        # Retrieve the article in dict form.
        article = services.get_article(article_id, repo.repo_instance)

        # Cause the web browser to display the page of all articles that have the same date as the commented article,
        # and display all comments, including the new comment.
        return redirect("/m?id="+str(article_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the article id, representing the article to comment, from a query parameter of the GET request.
        article_id = int(request.args.get('article'))

        # Store the article id in the form.
        form.article_id.data = article_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the article id of the article being commented from the form.
        article_id = int(form.article_id.data)

    # For a GET or an unsuccessful POST, retrieve the article to comment in dict form, and return a Web page that allows
    # the user to enter a comment. The generated Web page includes a form object.
    article = services.get_article(article_id, repo.repo_instance)
    return render_template(
        'home/comment_on_article.html',
        title='Edit article',
        article=article,
        form=form,
        handler_url=url_for('home_bp.comment_on_article'),
        tag_urls=utilities.get_tags_and_urls()
    )


def like(c, l, q):
    d = []
    for i in l:
        if i not in d and c["id"] != i["id"]:
            for f in [v['name'] for v in c["tags"]]:
                if f in [e['name'] for e in i["tags"]]:
                    if c["director"] == i["director"]:
                        d.insert(0, i)
                        break
                    else:
                        d.append(i)
                        break
    return d if len(d) > 0 else []


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', [
        DataRequired(),
        Length(min=4, message='Your comment is too short')])
    rating = SelectField('Rating', [DataRequired()], choices=[(i, i) for i in range(1,11)])
    article_id = HiddenField("Article id")
    submit = SubmitField('Submit')
