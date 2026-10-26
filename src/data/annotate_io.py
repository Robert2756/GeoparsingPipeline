import argparse
import re
from itertools import zip_longest
from pathlib import Path

from ..json_io import read_jsonl, write_jsonl
from src.schema import Annotation, Doc, Span, check_offsets

GOLD_DOCS = Path("data/gold/docs.jsonl")
GOLD_ANN = Path("data/gold/annotations_v1.jsonl")
MARK = re.compile(r"\[\[(.+?)(?:\|(\w+(?:,\w+)*))?\]\]")
LINE = re.compile(r"^([-+x])\s+(\S+)\s+(.*)$")
VALID_FLAGS = {"fig", "unsure", "hist"}


def sanitize(text: str) -> str:
    """Keep one snippet per line; replacements are 1:1 so offsets stay valid."""
    return text.replace("\t", " ").replace("\n", " ")


def parse_marked(marked: str) -> tuple[str, list[Span]]:
    parts, spans, pos, last = [], [], 0, 0
    for m in MARK.finditer(marked):
        pre = marked[last : m.start()]
        parts.append(pre)
        pos += len(pre)
        surface = m.group(1)
        flags = m.group(2).split(",") if m.group(2) else []
        bad = set(flags) - VALID_FLAGS
        if bad:
            raise ValueError(f"unknown flag(s) {bad} in: {m.group(0)}")
        spans.append(Span(start=pos, end=pos + len(surface), surface=surface,
                          source="human", flags=flags))
        parts.append(surface)
        pos += len(surface)
        last = m.end()
    parts.append(marked[last:])
    plain = "".join(parts)
    if "[[" in plain or "]]" in plain:
        raise ValueError(f"unbalanced [[ ]] in: {marked[:80]}")
    return plain, spans


def _load_existing() -> dict[str, Annotation]:
    return {a.doc_id: a for a in read_jsonl(GOLD_ANN, Annotation)} if GOLD_ANN.exists() else {}


def export_round(n: int, out: Path) -> None:
    docs = read_jsonl(GOLD_DOCS, Doc)
    done = set(_load_existing())
    cells: dict[tuple[str, str], list[Doc]] = {}
    for d in docs:
        if d.id not in done:
            cells.setdefault((d.lang, d.genre), []).append(d)
    # round-robin over language x genre cells, so every prefix is stratified
    order = [d for grp in zip_longest(*cells.values()) for d in grp if d is not None]
    lines = [f"-\t{d.id}\t{sanitize(d.text)}" for d in order[:n]]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(lines)} snippets to {out}")


def import_round(path: Path) -> None:
    docs = {d.id: d for d in read_jsonl(GOLD_DOCS, Doc)}
    existing = _load_existing()
    n_ok = n_excl = n_open = 0
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        m = LINE.match(line)
        if not m:
            raise ValueError(f"line {ln}: cannot parse (status / id / text)")
        status, doc_id, marked = m.groups()
        if status == "-":
            n_open += 1
            continue
        doc = docs[doc_id]
        if status == "x":
            existing[doc_id] = Annotation(doc_id=doc_id, annotator="gold_v1",
                                          spans=[], excluded=True)
            n_excl += 1
            continue
        plain, spans = parse_marked(marked)
        if plain != sanitize(doc.text):
            raise ValueError(f"line {ln} ({doc_id}): text changed outside the [[ ]] markup")
        ann = Annotation(doc_id=doc_id, annotator="gold_v1", spans=spans)
        check_offsets(doc, ann)
        existing[doc_id] = ann
        n_ok += 1
    write_jsonl(GOLD_ANN, existing.values())
    print(f"saved: {n_ok} annotated, {n_excl} excluded, {n_open} still open; "
          f"total in file: {len(existing)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--n", type=int, default=50)
    e.add_argument("--out", type=Path, default=Path("data/gold/annotate_round.txt"))
    i = sub.add_parser("import")
    i.add_argument("path", type=Path)
    a = ap.parse_args()
    export_round(a.n, a.out) if a.cmd == "export" else import_round(a.path)
    # python -m src.data.annotate_io export --n 50
    # python -m src.data.annotate_io import data/gold/annotate_round.txt