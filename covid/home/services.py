from typing import List, Iterable

from covid.adapters.repository import AbstractRepository
from covid.domain.model import make_comment, Article, Comment, Tag
from datetime import date, datetime

class NonExistentArticleException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_comment(article_id: int, comment_text: str, username: str, rating, repo: AbstractRepository):
    # Check that the article exists.
    article = repo.get_article(article_id)
    if article is None:
        raise NonExistentArticleException

    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    # Create comment.
    print(article)
    comment = make_comment(user, article, comment_text, rating)

    # Update the repository.
    repo.add_comment(comment)


def get_article(article_id: int, repo: AbstractRepository):
    article = repo.get_article(article_id)

    if article is None:
        raise NonExistentArticleException

    return article_to_dict(article)


def get_first_article(repo: AbstractRepository):

    article = repo.get_first_article()

    return article_to_dict(article)


def get_last_article(repo: AbstractRepository):

    article = repo.get_last_article()
    return article_to_dict(article)


def get_articles_by_date(date, repo: AbstractRepository):
    # Returns articles for the target date (empty if no matches), the date of the previous article (might be null), the date of the next article (might be null)

    articles = repo.get_articles_by_date(target_date=date)

    articles_dto = list()
    prev_date = next_date = None

    if len(articles) > 0:
        prev_date = repo.get_date_of_previous_article(articles[0])
        next_date = repo.get_date_of_next_article(articles[0])

        # Convert Articles to dictionary form.
        articles_dto = articles_to_dict(articles)

    return articles_dto, prev_date, next_date


def get_article_ids_for_tag(s, tag_name, repo: AbstractRepository):
    article_ids = repo.get_article_ids_for_tag(s, tag_name)

    return article_ids


def get_articles_by_id(id_list, repo: AbstractRepository):
    articles = repo.get_articles_by_id(id_list)

    # Convert Articles to dictionary form.
    articles_as_dict = articles_to_dict(articles)
    return articles_as_dict


def get_article_by_id(id_list, repo: AbstractRepository):
    articles = repo.get_articles_by_id(id_list)

    return article_to_dict(articles[0])


def get_article_by_id_similar(id_list, repo: AbstractRepository):
    articles = repo.get_articles_by_id(id_list)

    return [article_to_dict_sim(article) for article in articles]

def get_comments_for_article(article_id, repo: AbstractRepository):
    article = repo.get_article(article_id)

    if article is None:
        raise NonExistentArticleException

    return comments_to_dict(article.comments)


# ============================================
# Functions to convert model entities to dicts
# ============================================
def moviepage_to_dict(article: Article):
    article_dict = {
        'id': article.id,
        'title': article.title,
        'image_hyperlink': article.image_hyperlink
    }
    return article_dict


def article_to_dict(article: Article):
    print(article)
    article_dict = {
        'id': article.id,
        'date': article.date.year,
        'title': article.title,
        'first_para': article.first_para,
        'image_hyperlink': article.image_hyperlink,
        'back_hyperlink': article.back_hyperlink,
        'comments': comments_to_dict(article.comments),
        'tags': tags_to_dict(article.tags),
        'runtime': article.runtime,
        'rating': article.rating,
        'director': article.director,
        'actors': article.actors
    }
    return article_dict


def article_to_dict_sim(article: Article):
    article_dict = {
        'id': article.id,
        'title': article.title,
        'tags': tags_to_dict(article.tags),
        'director': article.director,
        'image_hyperlink': article.image_hyperlink
    }
    return article_dict


def articles_to_dict(articles: Iterable[Article]):
    return [moviepage_to_dict(article) for article in articles]


def comment_to_dict(comment: Comment):
    comment_dict = {
        'username': comment.user.username,
        'article_id': comment.article.id,
        'comment_text': comment.comment,
        'timestamp': comment.timestamp,
        'rating': comment.rating
    }
    return comment_dict


def comments_to_dict(comments: Iterable[Comment]):
    return [comment_to_dict(comment) for comment in comments]


def tag_to_dict(tag: Tag):
    tag_dict = {
        'name': tag.tag_name
        # 'tagged_articles': [article.id for article in tag.tagged_articles]
    }
    return tag_dict


def tags_to_dict(tags: Iterable[Tag]):
    return [tag_to_dict(tag) for tag in tags]


# ============================================
# Functions to convert dicts to model entities
# ============================================

def dict_to_article(dict):
    article = Article(dict.id, dict.date, dict.title, dict.first_para, dict.hyperlink)
    # Note there's no comments or tags.
    return article
