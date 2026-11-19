from parcel.knowledge import default_help_centre, tokenize


def test_all_articles_load_with_ids_and_titles():
    articles = default_help_centre().articles
    assert len(articles) == 14
    assert all(a.id.startswith("KB-") and a.title for a in articles)


def test_tokenize_drops_stop_words_and_stems():
    assert tokenize("How do I get my refunds?") == ["get", "refund"]


def test_delivery_question_finds_the_international_article_first():
    hits = default_help_centre().search("do you deliver to Spain")
    assert hits[0].article.id == "KB-113"


def test_known_retrieval_weakness_keyword_search_is_fooled_by_shared_words():
    """Kept on purpose for the retrieval lessons. 'long' matches 'as long as' in the
    returns article, so the refunds article only comes second."""
    ids = [h.article.id for h in default_help_centre().search("how long does a refund take")]
    assert ids[:2] == ["KB-104", "KB-105"]


def test_search_returns_at_most_k():
    assert len(default_help_centre().search("order delivery refund return", k=2)) == 2


def test_nonsense_finds_nothing():
    assert default_help_centre().search("zzzz qqqq") == []
