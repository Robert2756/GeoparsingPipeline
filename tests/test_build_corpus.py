from src.data.build_corpus import news_paragraphs

def test_news_stringified_list():
    long = "A" * 250
    assert news_paragraphs(str([long, "short"])) == [long]