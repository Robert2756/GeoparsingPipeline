from src.schema import Annotation, Doc, Span, check_offsets


def test_offsets_ok():
    doc = Doc(id="d1", lang="de", genre="news", text="Paris liegt an der Seine.")
    ann = Annotation(doc_id="d1", annotator="gold", spans=[
        Span(start=0, end=5, surface="Paris", source="human"),
        Span(start=19, end=24, surface="Seine", source="human"),
    ])
    check_offsets(doc, ann)