from typing import Literal

from pydantic import BaseModel


class Doc(BaseModel):              # represents an input document
    id: str
    lang: str                      # ISO 639-1, e.g. "de"
    genre: str                     # "wikipedia" | "news"
    text: str
    source_ref: str | None = None  # URL or title, needed for attribution

class Span(BaseModel):             # represents one place mention in a text, together with additional information
    start: int                     # character offset, inclusive
    end: int                       # character offset, exclusive
    surface: str                   # exact mention of the place in the text
    label: str = "LOC"             # label, e.g. "LOC" or "GPE"
    kb_id: str | None = None       # GeoNames ID, None = unresolved -> connection to external knowledge base
    lat: float | None = None
    lon: float | None = None
    confidence: float | None = None
    source: Literal["human", "llm", "model"]

class Annotation(BaseModel):       # groups multiple spans for a single document
    doc_id: str
    annotator: str                 # e.g. "gold_v1", "llama3.1-8b_fewshot"
    spans: list[Span]

def check_offsets(doc: Doc, ann: Annotation) -> None: # compare original text against annotation
    for s in ann.spans:
        if doc.text[s.start:s.end] != s.surface:
            raise ValueError(f"Offset mismatch in {doc.id}: {s}")