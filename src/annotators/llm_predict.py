import re
import sys
from pathlib import Path

from pydantic import BaseModel

from ..json_io import read_jsonl, write_jsonl
from ..schema import Annotation, Doc, Span

MODEL = "llama3.1:8b"

PROMPT = """Extract all geographic place names (toponyms) from the text. \
Answer as JSON: {"places": [...]} with each place name exactly as written in the text. \
Use an empty list if there are none.

Rules:
- Include countries, regions, states, cities, towns, villages, continents, islands, mountains, rivers, lakes and seas.
- Include short forms like US or UK when they mean the country.
- Include a country or city that stands for its government or team ("lost 0:1 against Spain").
- Give only the name: no article, preposition or possessive 's.
- Do NOT include demonyms or adjectives (German, schweizerisch).
- Do NOT include place names that are part of the name of an organization, party, team, event, work, title or person (Bank of England, Boston Celtics, Washington Irving).
- Do NOT include streets, buildings, stations, airports or named facilities such as mines, ranches or hotels.
- Do NOT include currency codes (US$) or fictional places.
- Only list places that are literally written in the text. Never add places that are merely implied.
- Words that do not reference the place but the name itself: similarity between the names of  "Swaziland" and "Switzerland".
- Place names inside phrases: "Viva España!" (Long live Spain!)"""


class Places(BaseModel):
    places: list[str]


def offsets_from_names(text: str, names: list[str]) -> list[tuple[int, int]]:
    """Mark every whole-word occurrence of each returned name; longest span wins on overlap."""
    found = []
    for name in dict.fromkeys(n.strip() for n in names if n.strip()):
        found += [(m.start(), m.end())
                  for m in re.finditer(rf"(?<!\w){re.escape(name)}(?!\w)", text)]
    found.sort(key=lambda x: (x[0], -(x[1] - x[0])))
    out, last_end = [], -1
    for s, e in found:
        if s >= last_end:
            out.append((s, e))
            last_end = e
    return out


def predict(doc: Doc, prompt: str, tag: str) -> Annotation:
    import ollama  # imported here so tests and CI don't need it

    resp = ollama.chat(
        model=MODEL,
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": f"Text: {doc.text}"}],
        format=Places.model_json_schema(),
        options={"temperature": 0, "seed": 0, "num_predict": 256,},
    )

    # print("Prompt: ", prompt)
    # print("Doc: ", doc.text)
    try:
        names = Places.model_validate_json(resp["message"]["content"]).places
    except ValueError:
        print(f"unparsable response for {doc.id}")
        names = []
    spans = [Span(start=s, end=e, surface=doc.text[s:e], source="llm")
             for s, e in offsets_from_names(doc.text, names)]
    return Annotation(doc_id=doc.id, annotator=tag, spans=spans)

    # stream = ollama.chat(
    #     model=MODEL,
    #     messages=[
    #         {"role": "system", "content": prompt},
    #         {"role": "user", "content": f"Text: {doc.text}"},
    #     ],
    #     format=Places.model_json_schema(),
    #     options={"temperature": 0, "seed": 0},
    #     stream=True,
    # )

    # response = ""
    # for chunk in stream:
    #     token = chunk["message"]["content"]
    #     print(token, end="", flush=True)
    #     response += token

    # print()  # newline after generation

    # try:
    #     names = Places.model_validate_json(response).places
    # except ValueError:
    #     print(f"Unparsable response for {doc.id}")
    #     names = []

if __name__ == "__main__":
    zero = len(sys.argv) > 1 and sys.argv[1] == "zero"  # no rules, first paragraph only
    prompt = PROMPT.split("\n\nRules")[0] if zero else PROMPT
    tag = "llm_zero" if zero else "llm_rules"

    annotated = {a.doc_id for a in read_jsonl(Path("data/gold/annotations_v1.jsonl"), Annotation)
                 if not a.excluded}
    docs = [d for d in read_jsonl(Path("data/gold/docs.jsonl"), Doc) if d.id in annotated]

    preds = []
    for i, d in enumerate(docs, 1):
        print(f"{i}/{len(docs)}: processing {d.id}", flush=True)
        preds.append(predict(d, prompt, tag))
        # if i % 20 == 0:
        #     print(f"{i}/{len(docs)}")
    write_jsonl(Path(f"data/predictions/{tag}.jsonl"), preds)
    print(f"saved {len(preds)} predictions to data/predictions/{tag}.jsonl")

# python -m src.annotators.llm_predict          # with rules
# python -m src.annotators.llm_predict zero     # without rules, the one comparison