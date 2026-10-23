import argparse
import ast
import random
from pathlib import Path

import pysbd # for the sentence segmenter
import yaml
from datasets import load_dataset

from src.io import write_jsonl
from src.schema import Doc

MIN_PARA_CHARS = 200
MIN_SNIPPET_CHARS, MAX_SNIPPET_CHARS = 150, 700
WIKI_CONFIG = "20231101.en"

# extract wiki paragraphs
def wiki_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n") if len(p.strip()) >= MIN_PARA_CHARS]


# extract news paragraphs
def news_paragraphs(raw) -> list[str]:
    if isinstance(raw, list):
        items = [str(x) for x in raw] # text is list
    else:
        s = str(raw).strip()
        items = None
        if s.startswith("["):
            try:
                v = ast.literal_eval(s) # parses the string as a Python literal and converts it into a real Python list
                if isinstance(v, list):
                    items = [str(x) for x in v] # string containing a Python expressio
            except (ValueError, SyntaxError):
                pass
        if items is None:
            items = s.split("\n") # string
    return [p.strip() for p in items if len(p.strip()) >= MIN_PARA_CHARS]


# creates random text snippet containing exactly n_sent consecutive sentences
def make_snippet(paras, seg, n_sent, rng): # rng -> random number generator
    paras = list(paras)
    rng.shuffle(paras)
    for para in paras:
        sents = [s.strip() for s in seg.segment(para) if s.strip()] # split each paragraph into sentences
        if len(sents) < n_sent: # if paragraph has not enough sentences skip
            continue
        i = rng.randrange(0, len(sents) - n_sent + 1) # valid starting positions: enough headroom so that the picked n_sents do not len(sents), + 1 since the max value is excluded
        snippet = " ".join(sents[i : i + n_sent]) # join the selected sentences
        if MIN_SNIPPET_CHARS <= len(snippet) <= MAX_SNIPPET_CHARS:
            return snippet
    return None


def wiki_articles(lang, seed):
    ds = load_dataset("wikimedia/wikipedia", WIKI_CONFIG.format(lang=lang),
                      split="train", streaming=True)
    for row in ds.shuffle(seed=seed, buffer_size=10_000):
        yield row["url"], wiki_paragraphs(row["text"])


def news_articles(news_ds, lang, seed):
    sub = news_ds.filter(lambda r: r["lang"] == lang).shuffle(seed=seed)
    for row in sub:
        yield row["url"], news_paragraphs(row["text"])


def build(cfg, out_dir: Path, dry_run: bool):
    d = cfg["data"]
    rng = random.Random(d["seed"])
    segs = {l: pysbd.Segmenter(language=l, clean=False) for l in d["languages"]} # segmenter for snippet builder
    news_ds = (load_dataset("Fumika/Wikinews-multilingual", split="train")
               if "news" in d["genres"] else None)
    gold_n, pool_n = d["gold_per_cell"], d["pool_per_cell"]
    gold, pool = [], []

    for genre in d["genres"]:
        for lang in d["languages"]: # process one of the four cells
            source = (wiki_articles(lang, d["seed"]) if genre == "wikipedia"
                      else news_articles(news_ds, lang, d["seed"]))
            docs = []
            for url, paras in source:  # one snippet per article -> no gold/pool leakage
                snip = make_snippet(paras, segs[lang], d["snippet_sentences"], rng)
                if snip:
                    docs.append(Doc(id=f"{lang}-{genre}-{len(docs):04d}", lang=lang,
                                    genre=genre, text=snip, source_ref=url))
                if len(docs) >= gold_n + pool_n:
                    break
            if len(docs) < gold_n + pool_n:
                print(f"WARNING {lang}/{genre}: only {len(docs)} of {gold_n + pool_n}")
            gold += docs[:gold_n] # first 40 documents
            pool += docs[gold_n:] # remaining documents
            print(f"{lang}/{genre}: gold={len(docs[:gold_n])} pool={len(docs[gold_n:])}")
            if dry_run: # inspect data without saving
                for doc in rng.sample(docs, min(3, len(docs))):
                    print("   -", doc.text[:250].replace("\n", " "))

    if not dry_run:
        write_jsonl(out_dir / "gold" / "docs.jsonl", gold)
        write_jsonl(out_dir / "pool" / "docs.jsonl", pool)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/default.yaml")
    ap.add_argument("--out", default="data")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    build(yaml.safe_load(open(a.config)), Path(a.out), a.dry_run)