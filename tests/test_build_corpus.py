from src.data.build_corpus import GLUED_RE, news_paragraphs, wiki_paragraphs


def test_news_stringified_list():
    long = "A" * 250
    assert news_paragraphs(str([long, "short"])) == [long] # "short" does not exceed the min amount of chars

def test_wiki_cuts_at_references():
    body = "X" * 250
    assert wiki_paragraphs(f"{body}\n\nReferences\n{'Y' * 250}") == [body]

def test_glued_sentences():
    assert GLUED_RE.sub(" ", "in the bin.The ASN released") == "in the bin. The ASN released"