from datetime import date

from covid.domain.model import User, Article, Tag, make_comment, make_tag_association, ModelException

import pytest


@pytest.fixture()
def article():
    return Article(
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
def tag():
    return Tag('Mystery')


def test_user_construction(user):
    assert user.username == 'dbowie'
    assert user.password == '1234567890'
    assert repr(user) == '<User dbowie 1234567890>'

    for comment in user.comments:
        # User should have an empty list of Comments after construction.
        assert False


def test_article_construction(article):
    assert article.id is None
    assert article.date == date.fromisoformat('2020-03-15')
    assert article.title == 'test movie'
    assert article.first_para == 'test movie fp'

    assert article.number_of_comments == 0
    assert article.number_of_tags == 0
    assert repr(
        article) == '<Article 2020-03-15 test movie>'


def test_article_less_than_operator():
    article_1 = Article(
        date.fromisoformat('2020-03-15'), "None", "None", "None", "None", 0.0, "None", 0, 0, "None", []
    )

    article_2 = Article(
        date.fromisoformat('2020-04-20'), "None", "None", "None", "None", 0.0, "None", 0, 0, "None", []
    )

    assert article_1 < article_2


def test_tag_construction(tag):
    assert tag.tag_name == 'Mystery'

    for article in tag.tagged_articles:
        assert False

    assert not tag.is_applied_to(Article(date.fromisoformat('2020-04-20'), "None", "None", "None", "None", 0.0, "None", 0, 0, "None", []))


def test_make_comment_establishes_relationships(article, user):
    comment_text = 'good film'
    comment = make_comment(user, article, comment_text, 8)

    # Check that the User object knows about the Comment.
    assert comment in user.comments

    # Check that the Comment knows about the User.
    assert comment.user is user

    # Check that Article knows about the Comment.
    assert comment in article.comments

    # Check that the Comment knows about the Article.
    assert comment.article is article


def test_make_tag_associations(article, tag):
    make_tag_association(article, tag)

    # Check that the Article knows about the Tag.
    assert article.is_tagged()
    assert article.is_tagged_by(tag)

    # check that the Tag knows about the Article.
    assert tag.is_applied_to(article)
    assert article in tag.tagged_articles


def test_make_tag_associations_with_article_already_tagged(article, tag):
    make_tag_association(article, tag)

    with pytest.raises(ModelException):
        make_tag_association(article, tag)
