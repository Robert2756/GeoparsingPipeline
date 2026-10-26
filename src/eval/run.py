import argparse
from pathlib import Path

from src.eval.metrics import evaluate, format_table
from ..json_io import read_jsonl
from src.schema import Annotation, Doc

ap = argparse.ArgumentParser()
ap.add_argument("--pred", type=Path, required=True)
ap.add_argument("--gold-docs", type=Path, default=Path("data/gold/docs.jsonl"))
ap.add_argument("--gold-ann", type=Path, default=Path("data/gold/annotations_v1.jsonl"))
a = ap.parse_args()

docs = read_jsonl(a.gold_docs, Doc)
gold = read_jsonl(a.gold_ann, Annotation)
pred = read_jsonl(a.pred, Annotation)
for mode in ("strict", "lenient"):
    print(f"\n== {mode}")
    print(format_table(evaluate(docs, gold, pred, mode)))

# python -m src.eval.run --pred data/predictions/llm_rules.jsonl
# python -m src.eval.run --pred data/predictions/llm_zero.jsonl